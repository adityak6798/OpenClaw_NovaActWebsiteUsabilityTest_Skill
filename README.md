# Nova Act Usability Testing Skill

AI-orchestrated usability testing for websites using Amazon Nova Act browser automation.

## What It Does

- **Adaptive Testing**: AI-driven browser automation that explores websites like a real user
- **Contextual Personas**: Analyzes your site and generates relevant user personas automatically
- **Realistic Test Cases**: Creates targeted test scenarios based on what your page actually offers
- **Iterative Exploration**: Tries multiple approaches per test (Nova Act requires exact text matching)
- **Comprehensive Reports**: Auto-generates HTML reports with detailed findings and session trace links

## Features

✅ **Real Browser Automation** - Actual Playwright browser control via Nova Act  
✅ **Smart Persona Generation** - Analyzes page content to create relevant user types  
✅ **Adaptive Testing** - AI tries multiple variations when element text doesn't match exactly  
✅ **Detailed Reporting** - Professional HTML reports with step-by-step observations  
✅ **Trace File Integration** - Links to Nova Act's HTML session recordings for replay  

## Requirements

- **Amazon Nova Act SDK** (`pip install nova-act`)
- **Playwright browsers** (`playwright install chromium`)
- **Nova Act API key** from AWS Console

## Installation

```bash
# Install via OpenClaw CLI
openclaw skill install nova-act-usability

# Or manually extract to skills directory
tar -xzf nova-act-usability.tar.gz -C ~/.openclaw/skills/
```

## Configuration

Create `~/.openclaw/config/nova-act.json`:

```json
{
  "apiKey": "your-nova-act-api-key-here"
}
```

Get your API key from the [AWS Console](https://console.aws.amazon.com/).

## Usage

Ask your OpenClaw agent:

```
Test https://example.com for usability
Run a usability test on example.com
```

The agent will:
1. Analyze the page structure
2. Generate contextual personas
3. Create realistic test cases
4. Run adaptive browser tests
5. Auto-generate an HTML report

## Example Output

**Test Results:**
- **Tech-savvy developer**: 3/3 tasks ✅ - Found docs, playground, value proposition
- **Business decision-maker**: 1/3 tasks - Found value prop, ❌ no pricing page, ❌ getting started not implemented
- **Beginner user**: 1/3 tasks - Found value prop, ❌ no tutorials, ❌ no help/support

**Report includes:**
- Executive summary with success rates
- Detailed step-by-step observations
- Links to Nova Act HTML trace files for session replay
- Recommendations for improvements

## How It Works

1. **Page Analysis**: Captures title, navigation, key elements
2. **Persona Generation**: Creates 3 contextual user types based on page content
3. **Test Case Creation**: Generates top 3 realistic tasks per persona
4. **Adaptive Execution**: Tries multiple prompt variations (Nova Act uses exact text matching)
5. **Report Generation**: Auto-creates comprehensive HTML report with trace links

## Nova Act Quirks

Nova Act uses **exact text matching** - if the page says "Docs" but you ask for "Documentation", it returns FALSE. This skill handles that by:
- Trying multiple variations per test ("Documentation" → "Docs" → "API" → "Developer")
- Iterative exploration rather than rigid scripts
- Logging all attempts for debugging

## Files

- `SKILL.md` - Main skill instructions for OpenClaw agents
- `scripts/run_adaptive_test.py` - Adaptive testing engine
- `scripts/enhanced_report_generator.py` - HTML report generator with trace links
- `scripts/trace_finder.py` - Extracts trace file paths from Nova Act output
- `references/nova-act-cookbook.md` - Nova Act usage patterns and quirks
- `references/persona-examples.md` - Sample personas for different site types
- `assets/report-template.html` - HTML report template

## Contributing

Found a bug? Have an improvement? Submit a PR or open an issue on GitHub.

## License

MIT

## Credits

Built for OpenClaw by Adi using Amazon Nova Act SDK.
