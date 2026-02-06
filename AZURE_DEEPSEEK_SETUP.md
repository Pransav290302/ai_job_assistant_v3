# Use Azure AI Foundry + DeepSeek R1 (No-Cost / Free Tier)

This project uses an **OpenAI-compatible** API for all AI features (resume analysis, tailored answers, resume extraction). You can run it with **Azure AI Foundry** and the **DeepSeek R1** model with no out-of-pocket cost by using Azure’s free credits.

## Why Azure AI Foundry + DeepSeek R1?

- **DeepSeek R1** is available in the [Azure AI Foundry](https://azure.microsoft.com/en-us/products/ai-foundry) model catalog.
- **New Azure accounts** get **$200 free credit** (no charge for 30 days; see [Azure account](https://azure.microsoft.com/en-us/pricing/purchase-options/azure-account)).
- **Microsoft Foundry** (formerly Azure AI Foundry) exposes an **OpenAI-compatible** endpoint, so this backend works without code changes: you only set environment variables.

## References

- **Blog:** [DeepSeek R1 is now available on Azure AI Foundry and GitHub](https://azure.microsoft.com/en-us/blog/deepseek-r1-is-now-available-on-azure-ai-foundry-and-github/)
- **YouTube:** [Deploy DeepSeek R1 using Azure AI Foundry and Build a Web Chatbot \| No Charges for API Use](https://www.youtube.com/watch?v=pj2knBX4S1w)
- **Docs:** [Tutorial: Get started with DeepSeek-R1 in Microsoft Foundry Models](https://learn.microsoft.com/en-us/azure/ai-foundry/model-inference/tutorials/get-started-deepseek-r1?tabs=python)
- **Billing:** [Azure free account](https://azure.microsoft.com/en-us/pricing/purchase-options/azure-account), [Billing for free trial](https://learn.microsoft.com/en-us/answers/questions/2283380/billing-for-free-trial-account)

---

## Step 1: Create an Azure account (if needed)

1. Go to [Azure account](https://azure.microsoft.com/en-us/pricing/purchase-options/azure-account).
2. Sign up; new customers get **$200 credit** for 30 days (no charge unless you exceed free limits).
3. A valid payment method may be required; you are not charged while staying within the free offer.

---

## Step 2: Deploy DeepSeek R1 in Microsoft Foundry

1. Open **Microsoft Foundry**: [https://ai.azure.com](https://ai.azure.com).
2. Sign in with your Azure account.
3. In the model catalog, search for **DeepSeek R1** (or **DeepSeek-R1**).
4. Open the model card and click **Deploy** (or **Use this model**).
5. Create a project if prompted; use defaults or customize.
6. In the deployment wizard:
   - **Deployment name:** e.g. `DeepSeek-R1` (you’ll use this as the model name in env).
   - **Deployment type:** e.g. Global Standard (default).
7. Click **Deploy** and wait until the deployment is ready.

---

## Step 3: Get endpoint URL and API key

1. When deployment finishes, open the deployment **Details** (or **Playground** → **Details**).
2. Note:
   - **Endpoint URI** — e.g. `https://YOUR-RESOURCE-NAME.openai.azure.com/openai/v1/`
   - **API key** — from the same page (e.g. “Key 1” or “API key”).

If you only see a resource name, the base URL is:

```text
https://<YOUR-RESOURCE-NAME>.openai.azure.com/openai/v1/
```

The **model** parameter in API calls must match your **deployment name** (e.g. `DeepSeek-R1`).

---

## Step 4: Configure this backend

In your backend root (e.g. `ai_job_backend/`), create or edit `.env` and set:

```env
# Azure AI Foundry – DeepSeek R1 (OpenAI-compatible)
OPENAI_BASE_URL=https://YOUR-RESOURCE-NAME.openai.azure.com/openai/v1/
OPENAI_API_KEY=your_api_key_from_foundry_deployment_details
OPENAI_MODEL=DeepSeek-R1
```

- Replace `YOUR-RESOURCE-NAME` with your actual resource name from the Foundry deployment.
- Replace `your_api_key_from_foundry_deployment_details` with the key from the deployment Details.
- Replace `DeepSeek-R1` with your deployment name if you chose a different one.

No code changes are required: the app already uses `OPENAI_BASE_URL`, `OPENAI_API_KEY`, and `OPENAI_MODEL` for all LLM calls (resume analysis, answer generation, resume extraction).

---

## Step 5: Run the backend

```bash
cd ai_job_backend
pip install -r requirements.txt
uvicorn api.main:app --reload
```

Or use your usual run command. The Assistant (Scrape Job, Analyze Resume, Generate Answer) will use DeepSeek R1 via Azure.

---

## Optional: Keyless auth (Microsoft Entra ID)

For production or CI, you can use **Microsoft Entra ID** instead of an API key:

1. Install: `pip install openai azure-identity`
2. Use a bearer token provider with `DefaultAzureCredential` and pass it as `api_key` to the OpenAI client (see [Use the model in code](https://learn.microsoft.com/en-us/azure/ai-foundry/model-inference/tutorials/get-started-deepseek-r1?tabs=python)).
3. This backend currently expects a single `OPENAI_API_KEY` string; to use Entra ID you’d need a small change to build the client with a token provider when `AZURE_USE_ENTRA_ID=true` (or similar). For local dev, the API key above is enough.

---

## Summary

| What you do | Where |
|-------------|--------|
| Create Azure account ($200 credit) | [Azure account](https://azure.microsoft.com/en-us/pricing/purchase-options/azure-account) |
| Deploy DeepSeek R1 | [Microsoft Foundry](https://ai.azure.com) → Model catalog → DeepSeek R1 → Deploy |
| Get endpoint + key | Deployment **Details** in Foundry |
| Configure backend | `.env`: `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL` |

After that, the AI Job Application Assistant uses the **free** DeepSeek R1 model on Azure AI Foundry with no code changes.
