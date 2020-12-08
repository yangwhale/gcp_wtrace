from google.cloud import bigquery

client = bigquery.Client(project="your-project-id")

df = client.query('''
SELECT metro, isp, max(ip) as ip
FROM `ds_us.agents`
WHERE v6 = false
and country = "BR"
and metro = "gru"
group by metro, isp
order by metro desc, isp
''' ).to_dataframe()
print(df.head(20))