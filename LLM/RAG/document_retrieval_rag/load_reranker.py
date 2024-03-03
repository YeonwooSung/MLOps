from sentence_transformers import CrossEncoder 
import numpy as np


cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# here we use some hard-coded documents, but in reality you would retrieve them from vector database or other search engine
retrieved_documents = [
    "The 2019–20 coronavirus pandemic is an ongoing pandemic of coronavirus disease 2019 (COVID-19) caused by severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2). The outbreak was first identified in Wuhan, Hubei, China, in December 2019, and was recognized as a pandemic by the World Health Organization (WHO) on 11 March 2020. As of 26 April 2020, more than 2.89 million cases of COVID-19 have been reported in 185 countries and territories, resulting in more than 202,000 deaths. More than 823,000 people have recovered, although there may be a possibility of relapse or reinfection. The virus is mainly spread during close contact and via respiratory droplets produced when people cough or sneeze. Respiratory droplets may be produced during breathing but the virus is not considered airborne. People may also catch COVID-19 by touching a contaminated surface and then their face.",
    "As of 26 April 2020, more than 2.89 million cases of COVID-19 have been reported in 185 countries and territories, resulting in more than 202,000 deaths. More than 823,000 people have recovered, although there may be a possibility of relapse or reinfection. The virus is mainly spread during close contact and via respiratory droplets produced when people cough or sneeze. Respiratory droplets may be produced during breathing but the virus is not considered airborne. People may also catch COVID-19 by touching a contaminated surface and then their face.",
    "Korea Centers for Disease Control and Prevention (KCDC) reported that the number of new cases in South Korea had dropped to 64, the lowest in about a month, and the number of recovered patients had exceeded that of new infections for the first time. The number of new cases in South Korea had dropped to 64, the lowest in about a month, and the number of recovered patients had exceeded that of new infections for the first time.",
    "Clearly, South Korea has been successful in flattening the curve. The number of new cases in South Korea had dropped to 64, the lowest in about a month, and the number of recovered patients had exceeded that of new infections for the first time.",
    "China has been praised for its response in Wuhan and Hubei. The Chinese government has been accused of significantly underreporting cases and deaths, and delaying its response. Wuhan and Hubei's governments have also been criticized for mishandling the initial outbreak. Numerous countries have evacuated their citizens from Wuhan and Hubei. The Chinese government has restricted travel within and out of Hubei and placed restrictions on the movement of people in other areas of northern China. Several provincial-level governments have declared a 'level one' response, the highest level of alert, in response to the outbreak. Many airlines have either cancelled or greatly reduced flights to China and several travel advisories now warn against travel to China. Mongolia closed its border with China and Hong Kong and Macau have placed a partial border closure and restrictions on travelers from mainland China. The outbreak has impacted the economy of China and other countries.",
]

query = "How many people have recovered from COVID-19?"

pairs = [[query, doc] for doc in retrieved_documents]
scores = cross_encoder.predict(pairs)

print("Scores:")
for score in scores:
    print(score)

print("New Ordering:") 
for o in np.argsort(scores)[::-1]:
    print(o+1)
