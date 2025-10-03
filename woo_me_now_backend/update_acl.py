import boto3

session = boto3.session.Session()
client = session.client(
    's3',
    region_name='nyc3',
    endpoint_url='https://nyc3.digitaloceanspaces.com',
    aws_access_key_id='DO801APJBTNNLPAR6A8J',
    aws_secret_access_key='hwLwZaaz0jQE00BgxMBq4waOaq47uzbbqSODMHHM9V4'
)
bucket_name = 'bucket-dcycle'
prefix = 'projects/woo_me_now/2025/media/'

# List and update ACLs
response = client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
for obj in response.get('Contents', []):
    print(f"Updating ACL for {obj['Key']}")
    client.put_object_acl(Bucket=bucket_name, Key=obj['Key'], ACL='public-read')