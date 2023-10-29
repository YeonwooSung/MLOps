from transformers import BertTokenizer, BertForMaskedLM
import torch
import timeit
import numpy as np
import torch_tensorrt
import torch.backends.cudnn as cudnn


enc = BertTokenizer.from_pretrained('bert-base-uncased')

batch_size = 4

batched_indexed_tokens = [[101, 64]*64]*batch_size
batched_segment_ids = [[0, 1]*64]*batch_size
batched_attention_masks = [[1, 1]*64]*batch_size

tokens_tensor = torch.tensor(batched_indexed_tokens)
segments_tensor = torch.tensor(batched_segment_ids)
attention_masks_tensor = torch.tensor(batched_attention_masks)

#
# Obtain a BERT masked language model from Hugging Face in the (scripted) TorchScript, then use the dummy inputs to trace it
#
mlm_model_ts = BertForMaskedLM.from_pretrained('bert-base-uncased', torchscript=True)
traced_mlm_model = torch.jit.trace(mlm_model_ts, [tokens_tensor, segments_tensor, attention_masks_tensor])


masked_sentences = [
    'Paris is the [MASK] of France.', 
    'The primary [MASK] of the United States is English.', 
    'A baseball game consists of at least nine [MASK].', 
    'Topology is a branch of [MASK] concerned with the properties of geometric objects that remain unchanged under continuous transformations.'
]
pos_masks = [4, 3, 9, 6]

encoded_inputs = enc(masked_sentences, return_tensors='pt', padding='max_length', max_length=128)
outputs = mlm_model_ts(**encoded_inputs)

most_likely_token_ids = [torch.argmax(outputs[0][i, pos, :]) for i, pos in enumerate(pos_masks)]

unmasked_tokens = enc.decode(most_likely_token_ids).split(' ')
unmasked_sentences = [masked_sentences[i].replace('[MASK]', token) for i, token in enumerate(unmasked_tokens)]

for sentence in unmasked_sentences:
    print(sentence)


encoded_inputs = enc(masked_sentences, return_tensors='pt', padding='max_length', max_length=128)
outputs = traced_mlm_model(encoded_inputs['input_ids'], encoded_inputs['token_type_ids'], encoded_inputs['attention_mask'])
most_likely_token_ids = [torch.argmax(outputs[0][i, pos, :]) for i, pos in enumerate(pos_masks)]

unmasked_tokens = enc.decode(most_likely_token_ids).split(' ')
unmasked_sentences = [masked_sentences[i].replace('[MASK]', token) for i, token in enumerate(unmasked_tokens)]

for sentence in unmasked_sentences:
    print(sentence)

#
# Compiling with Torch-TensorRT
# Change the logging level to avoid long printouts
#

new_level = torch_tensorrt.logging.Level.Error
torch_tensorrt.logging.set_reportable_log_level(new_level)

# Compile the model
trt_model = torch_tensorrt.compile(traced_mlm_model, 
    inputs= [torch_tensorrt.Input(shape=[batch_size, 128], dtype=torch.int32),  # input_ids
             torch_tensorrt.Input(shape=[batch_size, 128], dtype=torch.int32),  # token_type_ids
             torch_tensorrt.Input(shape=[batch_size, 128], dtype=torch.int32)], # attention_mask
    enabled_precisions= {torch.float32}, # Run with 32-bit precision
    workspace_size=2000000000,
    truncate_long_and_double=True
)


enc_inputs = enc(masked_sentences, return_tensors='pt', padding='max_length', max_length=128)
enc_inputs = {k: v.type(torch.int32).cuda() for k, v in enc_inputs.items()}

output_trt = trt_model(enc_inputs['input_ids'], enc_inputs['token_type_ids'], enc_inputs['attention_mask'])
most_likely_token_ids_trt = [torch.argmax(output_trt[i, pos, :]) for i, pos in enumerate(pos_masks)] 

unmasked_tokens_trt = enc.decode(most_likely_token_ids_trt).split(' ')
unmasked_sentences_trt = [masked_sentences[i].replace('[MASK]', token) for i, token in enumerate(unmasked_tokens_trt)]
for sentence in unmasked_sentences_trt:
    print(sentence)


trt_model_fp16 = torch_tensorrt.compile(traced_mlm_model, 
    inputs= [torch_tensorrt.Input(shape=[batch_size, 128], dtype=torch.int32),  # input_ids
             torch_tensorrt.Input(shape=[batch_size, 128], dtype=torch.int32),  # token_type_ids
             torch_tensorrt.Input(shape=[batch_size, 128], dtype=torch.int32)], # attention_mask
    enabled_precisions= {torch.half}, # Run with 16-bit precision
    workspace_size=2000000000,
    truncate_long_and_double=True
)


#
# Benchmarking
#

def timeGraph(model, input_tensor1, input_tensor2, input_tensor3, num_loops=50):
    print("Warm up ...")
    with torch.no_grad():
        for _ in range(20):
            features = model(input_tensor1, input_tensor2, input_tensor3)

    torch.cuda.synchronize()

    print("Start timing ...")
    timings = []
    with torch.no_grad():
        for i in range(num_loops):
            start_time = timeit.default_timer()
            features = model(input_tensor1, input_tensor2, input_tensor3)
            torch.cuda.synchronize()
            end_time = timeit.default_timer()
            timings.append(end_time - start_time)
            # print("Iteration {}: {:.6f} s".format(i, end_time - start_time))

    return timings

def printStats(graphName, timings, batch_size):
    times = np.array(timings)
    steps = len(times)
    speeds = batch_size / times
    time_mean = np.mean(times)
    time_med = np.median(times)
    time_99th = np.percentile(times, 99)
    time_std = np.std(times, ddof=0)
    speed_mean = np.mean(speeds)
    speed_med = np.median(speeds)

    msg = ("\n%s =================================\n"
            "batch size=%d, num iterations=%d\n"
            "  Median text batches/second: %.1f, mean: %.1f\n"
            "  Median latency: %.6f, mean: %.6f, 99th_p: %.6f, std_dev: %.6f\n"
            ) % (graphName,
                batch_size, steps,
                speed_med, speed_mean,
                time_med, time_mean, time_99th, time_std)
    print(msg)


cudnn.benchmark = True

timings = timeGraph(
    mlm_model_ts.cuda(),
    enc_inputs['input_ids'],
    enc_inputs['token_type_ids'],
    enc_inputs['attention_mask']
)
printStats("BERT", timings, batch_size)

timings = timeGraph(
    traced_mlm_model.cuda(),
    enc_inputs['input_ids'],
    enc_inputs['token_type_ids'],
    enc_inputs['attention_mask']
)
printStats("BERT", timings, batch_size)
