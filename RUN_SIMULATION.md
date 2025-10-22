# How to Run the Generative Agents Simulation

## ⚠️ Important: Python Version Requirement

This project requires **Python 3.9-3.11** (NOT Python 3.13+) because Django 2.2 is incompatible with newer Python versions.

✅ Your system is now set up with **Python 3.11** in the venv!

## Quick Start

### 1. Start the Environment Server (Terminal 1)

```bash
cd environment/frontend_server
source ../../venv/bin/activate
python manage.py runserver
```

**Expected output:**
```
Starting development server at http://127.0.0.1:8000/
```

**Verify:** Open http://localhost:8000/ in your browser - you should see "Your environment server is up and running"

---

### 2. Start the Simulation Server (Terminal 2)

```bash
cd reverie/backend_server
source ../../venv/bin/activate
python reverie.py
```

**You'll be prompted:**

1. **"Enter the name of the forked simulation:"**
   Type: `base_the_ville_isabella_maria_klaus`

2. **"Enter the name of the new simulation:"**
   Type: `test-simulation-gpt5` (or any name you want)

3. **"Enter option:"**
   Type: `run 100` (to run 100 steps = 1000 seconds = ~16 minutes game time)

---

### 3. Watch the Simulation

Open http://localhost:8000/simulator_home in your browser

You'll see:
- The 2D map of "Smallville"
- Isabella Rodriguez, Maria Lopez, and Klaus Mueller moving around
- Their activities and conversations
- Use arrow keys to navigate the map

---

## Simulation Commands

While the simulation server is running:

- `run <N>` - Run N steps (1 step = 10 seconds game time)
  - Example: `run 100` runs for 16.6 minutes game time
  - Example: `run 1000` runs for 2.77 hours game time

- `fin` - Save and exit the simulation

- `exit` - Exit without saving

---

## Cost Estimation

With GPT-5-nano ($0.05 per 1M input tokens, $0.40 per 1M output tokens):

- Each agent makes ~10-50 API calls per 100 steps
- Each call uses ~500-2000 tokens (input + output)
- **Estimated cost:** ~$0.01-0.05 per 100 steps for 3 agents

For 1000 steps (2.77 hours game time):
- **Estimated cost:** ~$0.10-0.50 total

**Much cheaper than the original GPT-3.5-turbo or GPT-4!**

---

## Troubleshooting

### Environment Server Won't Start

**Error:** `ModuleNotFoundError: No module named 'django'`
**Solution:**
```bash
source venv/bin/activate
pip install Django==2.2 django-cors-headers==2.5.3 numpy==1.25.2
```

### Simulation Server Error

**Error:** `ModuleNotFoundError: No module named 'openai'`
**Solution:**
```bash
source venv/bin/activate
pip install 'openai>=1.57.0' 'python-dotenv>=1.0.0'
```

### API Key Issues

**Error:** `401 Unauthorized` or `Invalid API key`
**Solution:** Check your `.env` file has the correct API key:
```bash
cat .env
# Should show: OPENAI_API_KEY=sk-proj-...
```

### Rate Limiting

If you hit OpenAI rate limits:
1. Save your simulation with `fin` command
2. Wait a few minutes
3. Resume by loading your saved simulation

---

## Replay a Saved Simulation

After saving with `fin`, replay it:

```
http://localhost:8000/replay/test-simulation-gpt5/1/
```

Replace:
- `test-simulation-gpt5` with your simulation name
- `1` with the starting step number

---

## Next Steps

- Try different prompts in `reverie/backend_server/persona/prompt_template/run_gpt_prompt.py`
- Add more agents by creating new persona folders
- Adjust agent personalities in their bootstrap memory files
- Monitor costs in your OpenAI dashboard

---

## System Status

✅ Python 3.11 venv created
✅ OpenAI SDK 2.5.0+ installed
✅ GPT-5-nano configured
✅ Structured outputs enabled
✅ All tests passed

**You're ready to run generative agent simulations!** 🎉
