from flask import Flask, request, jsonify, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
from functools import wraps
import time
import logging

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting
RATE_LIMIT = {'window': 60, 'max_requests': 30}
request_history = {}

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = request.remote_addr
        now = time.time()
        
        # Clean old requests
        request_history[ip] = [t for t in request_history.get(ip, []) if now - t < RATE_LIMIT['window']]
        
        if len(request_history.get(ip, [])) >= RATE_LIMIT['max_requests']:
            return jsonify({'error': 'Too many requests'}), 429
        
        request_history.setdefault(ip, []).append(now)
        return f(*args, **kwargs)
    return decorated_function

# Financial knowledge base
RESPONSES = {
    "loan": {
        "personal": "Personal loans typically have interest rates between 10.5% to 24%. Key information:\n\n"
                   "Requirements:\n"
                   "- Valid ID proof (Passport, Aadhaar, PAN)\n"
                   "- Proof of income (Salary slips, Form 16)\n"
                   "- Bank statements (Last 6 months)\n"
                   "- Credit score check (Usually 750+ preferred)\n\n"
                   "Processing Time:\n"
                   "- 2-7 business days typically\n"
                   "- Instant approval for pre-qualified customers\n\n"
                   "Loan Amount:\n"
                   "- Usually ranges from ₹50,000 to ₹40 lakhs\n"
                   "- Amount depends on income and credit score\n\n"
                   "Repayment Tenure:\n"
                   "- Typically ranges from 12 to 60 months\n"
                   "- Can be extended up to 5 years in some cases\n\n"
                   "Fees and Charges:\n"
                   "- Processing fees (up to 2% of loan amount)\n"
                   "- Prepayment charges (up to 5% of outstanding amount)",
        
        "home": "Home loans (mortgages) usually have rates from 6.5% to 9.5%. Important details:\n\n"
                "Requirements:\n"
                "- Property documentation\n"
                "- Income proof (ITR for 2-3 years)\n"
                "- Credit score (Preferably 750+)\n"
                "- Down payment (Usually 20% of property value)\n\n"
                "Benefits:\n"
                "- Tax benefits under Section 80C and 24(b)\n"
                "- Lower interest rates compared to personal loans\n"
                "- Longer repayment tenure (up to 30 years)\n\n"
                "Types:\n"
                "- Fixed Rate: Rate remains constant\n"
                "- Floating Rate: Rate changes with market\n"
                "- Hybrid: Fixed for initial years, then floating\n\n"
                "Additional Costs:\n"
                "- Stamp duty and registration charges\n"
                "- Property valuation fees\n"
                "- Processing fees",
        
        "business": "Business loans vary by type and size. Key aspects:\n\n"
                   "Requirements:\n"
                   "- Business plan and projections\n"
                   "- Financial statements (2-3 years)\n"
                   "- GST returns\n"
                   "- Bank statements\n"
                   "- Credit history\n"
                   "- Collateral (for secured loans)\n\n"
                   "Types:\n"
                   "- Term Loans: Fixed amount, regular repayment\n"
                   "- Working Capital Loans: For day-to-day operations\n"
                   "- Equipment Financing: Specifically for machinery\n"
                   "- Invoice Financing: Based on unpaid invoices\n\n"
                   "Interest Rates:\n"
                   "- MSME loans: 8-16%\n"
                   "- Secured business loans: 11-16%\n"
                   "- Unsecured business loans: 15-24%\n\n"
                   "Repayment Options:\n"
                   "- Monthly installments\n"
                   "- Quarterly payments\n"
                   "- Bullet payments",
        
        "education": "Education loans help fund higher studies. Details:\n\n"
                    "Coverage:\n"
                    "- Tuition fees\n"
                    "- Living expenses\n"
                    "- Books and equipment\n"
                    "- Travel expenses\n\n"
                    "Features:\n"
                    "- Interest rates: 8.5-15%\n"
                    "- Moratorium period during study\n"
                    "- Tax benefits under Section 80E\n"
                    "- Collateral may be required for loans above ₹7.5 lakhs\n\n"
                    "Repayment Terms:\n"
                    "- Repayment starts after moratorium period\n"
                    "- Loan tenure up to 15 years\n"
                    "- Part payment and prepayment allowed",
    },
    
    "credit": {
        "score": "CIBIL score ranges from 300-900. Understanding your score:\n\n"
                 "Score Ranges:\n"
                 "- 750+ : Excellent - Best loan rates\n"
                 "- 700-749: Good - Likely to get loans\n"
                 "- 650-699: Fair - May get loans at higher rates\n"
                 "- Below 650: Poor - Difficult to get loans\n\n"
                 "Impact:\n"
                 "- Loan approval chances\n"
                 "- Interest rates offered\n"
                 "- Credit card limits\n"
                 "- Employment (some employers check)\n\n"
                 "Factors Affecting Score:\n"
                 "- Payment history (35%)\n"
                 "- Credit utilization (30%)\n"
                 "- Credit mix (15%)\n"
                 "- New credit (10%)\n"
                 "- Credit history length (10%)",
        
        "report": "A credit report shows your credit history:\n\n"
                  "Key Components:\n"
                  "1. Personal Information\n"
                  "   - Name, DOB, PAN, addresses\n\n"
                  "2. Credit Account Information\n"
                  "   - Credit cards\n"
                  "   - Loans\n"
                  "   - Payment history\n"
                  "   - Credit limits\n\n"
                  "3. Enquiries\n"
                  "   - Hard enquiries (loan applications)\n"
                  "   - Soft enquiries (self-checks)\n\n"
                  "4. Public Records\n"
                  "   - Defaults\n"
                  "   - Legal suits\n"
                  "   - Bankruptcies\n\n"
                  "How to Read:\n"
                  "- Check for errors\n"
                  "- Understand credit score\n"
                  "- Analyze credit history",
        
        "improvement": "To improve credit score:\n\n"
                      "Essential Steps:\n"
                      "1. Payment History (35% impact)\n"
                      "   - Pay all bills on time\n"
                      "   - Set up auto-payments\n"
                      "   - Clear any defaults\n\n"
                      "2. Credit Utilization (30% impact)\n"
                      "   - Keep below 30%\n"
                      "   - Increase credit limits\n"
                      "   - Pay credit card bills in full\n\n"
                      "3. Credit Mix (15% impact)\n"
                      "   - Have a mix of credit types\n"
                      "   - Maintain old accounts\n\n"
                      "4. New Credit (10% impact)\n"
                      "   - Limit new applications\n"
                      "   - Space out credit requests\n\n"
                      "5. Credit History Length (10% impact)\n"
                      "   - Keep old accounts active\n"
                      "   - Don't close oldest cards\n\n"
                      "Additional Tips:\n"
                      "- Monitor credit report regularly\n"
                      "- Avoid negative marks\n"
                      "- Build a long credit history",
        
        "monitoring": "Monitor your credit regularly:\n\n"
                     "Free Methods:\n"
                     "- Annual free credit report\n"
                     "- Credit score monitoring apps\n"
                     "- Bank-provided services\n\n"
                     "What to Monitor:\n"
                     "- Unauthorized accounts\n"
                     "- Incorrect information\n"
                     "- Payment records\n"
                     "- Credit utilization\n\n"
                     "Frequency:\n"
                     "- Check score monthly\n"
                     "- Full report quarterly\n"
                     "- Dispute errors immediately\n\n"
                     "Benefits:\n"
                     "- Early detection of errors\n"
                     "- Prevention of identity theft\n"
                     "- Better credit score management",
    },
    
    "investment": {
        "stocks": "Stock market investments:\n\n"
                  "Types:\n"
                  "- Direct Equity\n"
                  "- Mutual Funds\n"
                  "- ETFs\n"
                  "- Index Funds\n\n"
                  "Risk Level: High\n"
                  "Expected Returns: 12-15% p.a.\n\n"
                  "Getting Started:\n"
                  "1. Open Demat account\n"
                  "2. Start with blue-chip stocks\n"
                  "3. Diversify portfolio\n"
                  "4. Consider SIP for mutual funds\n\n"
                  "Investment Strategies:\n"
                  "- Long-term investing\n"
                  "- Dollar-cost averaging\n"
                  "- Value investing\n"
                  "- Growth investing",
        
        "bonds": "Bond investments:\n\n"
                 "Types:\n"
                 "- Government Bonds\n"
                 "- Corporate Bonds\n"
                 "- Treasury Bills\n"
                 "- Fixed Deposits\n\n"
                 "Risk Level: Low to Medium\n"
                 "Expected Returns: 5-8% p.a.\n\n"
                 "Features:\n"
                 "- Regular interest payments\n"
                 "- Fixed maturity date\n"
                 "- Lower risk than stocks\n\n"
                 "Investment Options:\n"
                 "- Direct investment\n"
                 "- Mutual funds\n"
                 "- Exchange-traded funds (ETFs)",
        
        "mutual_funds": "Mutual Fund investments:\n\n"
                       "Types:\n"
                       "1. Equity Funds\n"
                       "   - Large Cap\n"
                       "   - Mid Cap\n"
                       "   - Small Cap\n\n"
                       "2. Debt Funds\n"
                       "   - Liquid Funds\n"
                       "   - Income Funds\n\n"
                       "3. Hybrid Funds\n"
                       "   - Balanced Funds\n"
                       "   - Monthly Income Plans\n\n"
                       "Investment Options:\n"
                       "- Lump sum\n"
                       "- SIP (Systematic Investment Plan)\n"
                       "- STP (Systematic Transfer Plan)\n\n"
                       "Benefits:\n"
                       "- Diversification\n"
                       "- Professional management\n"
                       "- Liquidity\n"
                       "- Tax benefits",
    },
    
    "insurance": {
        "life": "Life Insurance policies:\n\n"
                "Types:\n"
                "1. Term Insurance\n"
                "   - Pure risk coverage\n"
                "   - Lower premiums\n"
                "   - No maturity benefit\n\n"
                "2. Endowment Plans\n"
                "   - Insurance + Savings\n"
                "   - Higher premiums\n"
                "   - Maturity benefits\n\n"
                "3. ULIPs\n"
                "   - Insurance + Investment\n"
                "   - Market-linked returns\n"
                "   - Lock-in period\n\n"
                "Key Features:\n"
                "- Death benefit\n"
                "- Maturity benefit\n"
                "- Tax benefits\n"
                "- Riders (additional benefits)",
        
        "health": "Health Insurance coverage:\n\n"
                  "Types:\n"
                  "1. Individual Health Plan\n"
                  "2. Family Floater\n"
                  "3. Critical Illness Cover\n"
                  "4. Senior Citizen Plans\n\n"
                  "Key Features:\n"
                  "- Cashless treatment\n"
                  "- Pre/post hospitalization\n"
                  "- No-claim bonus\n"
                  "- Tax benefits u/s 80D\n\n"
                  "Additional Covers:\n"
                  "- Top-up plans\n"
                  "- Super top-up plans\n"
                  "- Critical illness riders",
        
        "vehicle": "Vehicle Insurance types:\n\n"
                   "1. Third-party Liability (Mandatory)\n"
                   "   - Covers damage to others\n"
                   "   - Legal requirement\n\n"
                   "2. Comprehensive Cover\n"
                   "   - Own damage protection\n"
                   "   - Third-party liability\n"
                   "   - Additional riders available\n\n"
                   "Add-on Covers:\n"
                   "- Zero depreciation\n"
                   "- Engine protection\n"
                   "- Roadside assistance\n\n"
                   "Key Features:\n"
                   "- Cashless claims\n"
                   "- 24x7 assistance\n"
                   "- Transfer of no-claim bonus",
    },
    
    "tax": {
        "gst": "GST (Goods and Services Tax) Information:\n\n"
                "1. What is GST?\n"
                "- A comprehensive indirect tax on manufacture, sale and consumption\n"
                "- Replaced multiple cascading taxes levied by central and state governments\n"
                "- Implemented on July 1, 2017\n\n"
                "2. GST Rates:\n"
                "- 0% (Essential items)\n"
                "- 5% (Basic necessities)\n"
                "- 12% (Standard rate 1)\n"
                "- 18% (Standard rate 2)\n"
                "- 28% (Luxury items)\n\n"
                "3. Key Features:\n"
                "- Input tax credit available\n"
                "- Electronic compliance system\n"
                "- Unified market across India\n"
                "- Regular filing of returns required",
        
        "income": "Income Tax Information:\n"
                  "- Progressive tax system\n"
                  "- Tax slabs based on income\n"
                  "- Various deductions available\n"
                  "- Quarterly advance tax payments",
        
        "saving": "Tax Saving Options:\n"
                  "- Section 80C investments\n"
                  "- PPF and ELSS\n"
                  "- Home loan benefits\n"
                  "- Health insurance premium"
    },
    
    "interest": {
        "types": """Common interest types:
- Fixed Rate: Rate remains constant
- Floating Rate: Rate changes with market
- Flat Rate: Calculated on full loan amount

Interest can be:
- Simple Interest: P × R × T
- Compound Interest: P(1 + R)^T - P
Where P=Principal, R=Rate, T=Time

Current rates by loan type:
- Home Loan: 6.5-9.5%
- Personal Loan: 10.5-24%
- Car Loan: 7.5-15%
- Education Loan: 8.5-15%""",
        
        "calculation": """Interest Calculation Methods:

1. Simple Interest (SI):
- Formula: SI = P × R × T
- Where: P = Principal, R = Rate, T = Time
- Used for: Short-term loans, FDs

2. Compound Interest (CI):
- Formula: CI = P(1 + R)^T - P
- Compounds: Monthly, Quarterly, Yearly
- Used for: Long-term loans, investments

3. Reducing Balance:
- Interest calculated on remaining principal
- EMI = P × R × (1+R)^N/((1+R)^N-1)
- Used for: Most retail loans

4. Examples:
- FD: Usually Simple Interest
- Home Loan: Reducing Balance
- Credit Card: Monthly Compound Interest"""
    }
}

keyword_map = {
    'gst': ('tax', 'gst'),
    'what is gst': ('tax', 'gst'),
    'goods and services tax': ('tax', 'gst'),
    'gst rates': ('tax', 'gst'),
    'gst information': ('tax', 'gst'),
    
    "loan": ("loan", "personal"),
    "loans": ("loan", "personal"),
    "personal loan": ("loan", "personal"),
    "home loan": ("loan", "home"),
    "business loan": ("loan", "business"),
    "education loan": ("loan", "education"),
    "credit score": ("credit", "score"),
    "credit report": ("credit", "report"),
    "credit improvement": ("credit", "improvement"),
    "credit monitoring": ("credit", "monitoring"),
    "investment": ("investment", "stocks"),
    "investments": ("investment", "stocks"),
    "stock market": ("investment", "stocks"),
    "stocks": ("investment", "stocks"),
    "bonds": ("investment", "bonds"),
    "mutual funds": ("investment", "mutual_funds"),
    "insurance": ("insurance", "life"),
    "life insurance": ("insurance", "life"),
    "health insurance": ("insurance", "health"),
    "vehicle insurance": ("insurance", "vehicle"),
    "tax": ("tax", "gst"),
    "income tax": ("tax", "income"),
    "tax saving": ("tax", "saving"),
    "interest": ("interest", "types"),
    "interest types": ("interest", "types"),
    "interest calculation": ("interest", "calculation"),
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
@rate_limit
def chat():
    try:
        # Get and validate input
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
            
        user_message = request.json.get('message', '')
        if not isinstance(user_message, str):
            return jsonify({'error': 'Message must be a string'}), 400
            
        # Limit message length
        if len(user_message) > 500:  # Adjust limit as needed
            return jsonify({'error': 'Message too long'}), 400
            
        # Clean and normalize user input
        user_message = user_message.lower()
        user_message = user_message.strip('"\'')
        user_message = ''.join(c for c in user_message if c.isalnum() or c.isspace())
        user_message = user_message.strip()
        
        if not user_message:
            return jsonify({'error': 'Please provide a message'}), 400
        
        # Default welcome message
        default_response = ("I'm here to help with your financial questions. You can ask about:\n\n"
                          "1. Loans (personal, home, business, education)\n"
                          "2. Credit (score, report, improvement tips)\n"
                          "3. Investments (stocks, bonds, mutual funds)\n"
                          "4. Insurance (life, health, vehicle)\n"
                          "5. Tax and GST\n\n"
                          "How can I assist you today?")
        
        # Find matching category and subcategory
        category = None
        subcategory = None
        
        # First try exact phrase matching
        if user_message in keyword_map:
            category, subcategory = keyword_map[user_message]
        else:
            # Then try partial matching
            for keyword, (cat, subcat) in keyword_map.items():
                if keyword in user_message:
                    category = cat
                    subcategory = subcat
                    break
        
        # If no match found, return default response
        if not category:
            return jsonify({'response': default_response})
        
        # Get response based on category and subcategory
        if subcategory and subcategory in RESPONSES.get(category, {}):
            response = RESPONSES[category][subcategory]
        else:
            # If no specific subcategory or subcategory not found, return all info from category
            if category in RESPONSES:
                response = "\n\n".join(RESPONSES[category].values())
            else:
                response = default_response
        
        return jsonify({'response': response})
            
    except ValueError as e:
        logger.error(f"ValueError in chat endpoint: {str(e)}")
        return jsonify({'error': 'Invalid input provided'}), 400
    except KeyError as e:
        logger.error(f"KeyError in chat endpoint: {str(e)}")
        return jsonify({'error': 'Required data missing'}), 400
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        return jsonify({'error': 'An internal error occurred'}), 500

if __name__ == '__main__':
    # Only use debug mode in development
    is_development = True  # Change this based on environment variable in production
    if is_development:
        app.run(debug=True, host='127.0.0.1', port=5000)
    else:
        app.run(host='0.0.0.0', port=5000)