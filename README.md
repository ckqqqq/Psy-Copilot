### DataJarvis

Environment

```
conda create -n py38 python==3.8
conda activate py38
pip install -r requirements.txt
```

Load PGSQL PASSWORD

1. create a file ".env" at "DATAJARVIS" floder.
2. input PGSQL_PASSWARD=xxxxxx in .env file
Key vault can befound in [pgsql-bingviz-metrics-storage key](https://ms.portal.azure.com/?l=en.en-us#view/Microsoft_Azure_KeyVault/ListObjectVersionsRBACBlade/~/overview/objectType/secrets/objectId/https%3A%2F%2Fbv-core-development.vault.azure.net%2Fsecrets%2Fpgsql-bingviz-metrics-storage/vaultResourceUri/%2Fsubscriptions%2F700e6ae5-eded-4e62-b94f-0d68f0fc591c%2FresourceGroups%2FDev-BingViz-KeyVaults%2Fproviders%2FMicrosoft.KeyVault%2Fvaults%2FBV-Core-Development/vaultId/%2Fsubscriptions%2F700e6ae5-eded-4e62-b94f-0d68f0fc591c%2FresourceGroups%2FDev-BingViz-KeyVaults%2Fproviders%2FMicrosoft.KeyVault%2Fvaults%2FBV-Core-Development)
```
   PGSQL_PASSWARD=xxxxxx
   ```

Run

```python
streamlit run .\Main_V2.py
```
