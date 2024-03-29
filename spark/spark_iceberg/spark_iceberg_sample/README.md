# Spark Iceberg Sample

This sample demonstrates how to use Iceberg with Spark.

## Running instruction

Start up the docker containers with this command:

```bash
docker-compose up
```

You can then run any of the following commands to start a Spark session.

```bash
# Spark SQL
docker exec -it spark-iceberg spark-sql

# Spark Shell
docker exec -it spark-iceberg spark-shell

# PySpark Shell
docker exec -it spark-iceberg spark-shell
```

To create your first Iceberg table in Spark, run a CREATE TABLE command.
Let's create a table using demo.nyc.taxis where demo is the catalog name, nyc is the database name, and taxis is the table name.

Spark SQL:
```sql
CREATE TABLE demo.nyc.taxis
(
  vendor_id bigint,
  trip_id bigint,
  trip_distance float,
  fare_amount double,
  store_and_fwd_flag string
)
PARTITIONED BY (vendor_id);
```

Spark Shell:
```scala
import org.apache.spark.sql.types._
import org.apache.spark.sql.Row
val schema = StructType( Array(
    StructField("vendor_id", LongType,true),
    StructField("trip_id", LongType,true),
    StructField("trip_distance", FloatType,true),
    StructField("fare_amount", DoubleType,true),
    StructField("store_and_fwd_flag", StringType,true)
))
val df = spark.createDataFrame(spark.sparkContext.emptyRDD[Row],schema)
df.writeTo("demo.nyc.taxis").create()
```

PySpark:
```python
from pyspark.sql.types import DoubleType, FloatType, LongType, StructType,StructField, StringType
schema = StructType([
  StructField("vendor_id", LongType(), True),
  StructField("trip_id", LongType(), True),
  StructField("trip_distance", FloatType(), True),
  StructField("fare_amount", DoubleType(), True),
  StructField("store_and_fwd_flag", StringType(), True)
])

df = spark.createDataFrame([], schema)
df.writeTo("demo.nyc.taxis").create()
```

Once your table is created, you can insert records.

Spark SQL:
```sql
INSERT INTO demo.nyc.taxis
VALUES (1, 1000371, 1.8, 15.32, 'N'), (2, 1000372, 2.5, 22.15, 'N'), (2, 1000373, 0.9, 9.01, 'N'), (1, 1000374, 8.4, 42.13, 'Y');
```

Spark Shell:
```scala
import org.apache.spark.sql.Row

val schema = spark.table("demo.nyc.taxis").schema
val data = Seq(
    Row(1: Long, 1000371: Long, 1.8f: Float, 15.32: Double, "N": String),
    Row(2: Long, 1000372: Long, 2.5f: Float, 22.15: Double, "N": String),
    Row(2: Long, 1000373: Long, 0.9f: Float, 9.01: Double, "N": String),
    Row(1: Long, 1000374: Long, 8.4f: Float, 42.13: Double, "Y": String)
)
val df = spark.createDataFrame(spark.sparkContext.parallelize(data), schema)
df.writeTo("demo.nyc.taxis").append()
```

PySpark:
```python
from pyspark.sql import Row
schema = spark.table("demo.nyc.taxis").schema
data = [
    (1, 1000371, 1.8, 15.32, "N"),
    (2, 1000372, 2.5, 22.15, "N"),
    (2, 1000373, 0.9, 9.01, "N"),
    (1, 1000374, 8.4, 42.13, "Y")
  ]
df = spark.createDataFrame(data, schema)
df.writeTo("demo.nyc.taxis").append()
```

If you already have a Spark environment, you can add Iceberg, using the --packages option.

```bash
# Spark SQL
spark-sql --packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.0

# Spark Shell
spark-shell --packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.0

# PySpark Shell
pyspark --packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.0
```

## References

- [Iceberg: Spark Quickstart](https://iceberg.apache.org/spark-quickstart/)
