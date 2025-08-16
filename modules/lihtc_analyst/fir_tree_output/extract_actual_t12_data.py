#!/usr/bin/env python3
"""
Extract actual T-12 data from Fir Tree PDF
Period: Jun 2024 - May 2025 (12 months actual)
Column B (Titles) and Column O (Totals)
"""

def extract_t12_actual_data():
    """Extract the actual T-12 12-month totals"""
    
    print("🏛️ FIR TREE T-12 ACTUAL DATA EXTRACTION")
    print("=" * 50)
    print("📅 Period: Jun 2024 - May 2025 (12 months)")
    print("📊 Source: Column O totals from T-12 statement")
    print()
    
    # INCOME DATA (from PDF Column O)
    income_data = {
        "Total Income": 522829.00,
        "Net Rental Income": 519402.00,
        "Market Rent": 296441.00,
        "Tenant Subsidy": 230347.00,
        "Other Income": 3427.00,
    }
    
    # EXPENSE DATA (from PDF Column O) - organized by major categories
    expense_data = {
        # Repairs & Maintenance
        "Total Repairs & Maintenance": 5838.07,
        
        # Utilities (Owner Paid)
        "Total Utilities": 110291.80,
        "Water": 13153.01,
        "Trash": 8027.63,
        "Electric": 43089.98,
        "Sewer": 43328.95,
        "Storm/Drainage": 2692.23,
        
        # Advertising & Promotion
        "Total Advertising & Promotion": 5447.32,
        
        # Cleaning & Supplies
        "Total Cleaning & Supplies": 1349.42,
        
        # Salaries & Wages
        "Total Salaries & Wages": 186703.51,
        "Manager's Salary": 71861.62,
        "Medical Insurance": 14996.62,
        "Maintenance Supervisor Salary": 62872.72,
        "Payroll Taxes": 17480.37,
        
        # Insurance
        "Total Insurance": 39952.10,
        "Fire & Extended Coverage": 39952.10,
        
        # Management/Asset Mgmt Fees
        "Total Management/Asset Mgmt Fees": 38929.00,
        "Professional Management Fee": 38929.00,
        
        # Administrative
        "Total Administrative": 21804.88,
        "Telephone": 5561.76,
        "Computer": 6007.67,
        "Training": 2357.44,
        
        # Legal & Accounting
        "Total Legal & Accounting": 8204.20,
        "Accounting": 11335.00,
        
        # MAJOR TOTALS
        "Total Operating Expenses": 418520.30,
        "Net Operating Income": 104308.69,
        
        # Non-Routine Maintenance
        "Total Non-Routine Maintenance": -6372.95,  # Credit back
        
        # Interest & Financial
        "Total Interest & Other Financial": 22006.46,
        
        # Final Net Income
        "Net Income": 22697.68
    }
    
    # Calculate per unit per month figures (60 units)
    print("📊 INCOME BREAKDOWN (T-12 Actual)")
    print("-" * 40)
    for item, amount in income_data.items():
        per_unit_month = round(amount / 60 / 12, 0) if amount != 0 else 0
        print(f"{item:.<35} ${amount:>10,.0f} (${per_unit_month}/unit/month)")
    
    print()
    print("💸 EXPENSE BREAKDOWN (T-12 Actual)")
    print("-" * 40)
    
    # Group expenses by category for better presentation
    major_categories = [
        ("Utilities (Owner Paid)", ["Total Utilities", "Electric", "Sewer", "Water", "Trash", "Storm/Drainage"]),
        ("Salaries & Wages", ["Total Salaries & Wages", "Manager's Salary", "Maintenance Supervisor Salary", "Medical Insurance", "Payroll Taxes"]),
        ("Insurance", ["Total Insurance", "Fire & Extended Coverage"]),
        ("Management Fees", ["Total Management/Asset Mgmt Fees", "Professional Management Fee"]),
        ("Administrative", ["Total Administrative", "Telephone", "Computer", "Training"]),
        ("Legal & Accounting", ["Total Legal & Accounting", "Accounting"]),
        ("Repairs & Maintenance", ["Total Repairs & Maintenance"]),
        ("Other Categories", ["Total Advertising & Promotion", "Total Cleaning & Supplies"])
    ]
    
    for category_name, items in major_categories:
        print(f"\n🏷️  {category_name}:")
        for item in items:
            if item in expense_data:
                amount = expense_data[item]
                per_unit_month = round(amount / 60 / 12, 0) if amount != 0 else 0
                indent = "    " if not item.startswith("Total") else "  "
                print(f"{indent}{item:.<32} ${amount:>10,.0f} (${per_unit_month}/unit/month)")
    
    print()
    print("🎯 KEY TOTALS (T-12 Actual)")
    print("-" * 40)
    key_totals = [
        "Total Operating Expenses",
        "Net Operating Income", 
        "Total Non-Routine Maintenance",
        "Total Interest & Other Financial",
        "Net Income"
    ]
    
    for item in key_totals:
        if item in expense_data:
            amount = expense_data[item]
            per_unit_month = round(amount / 60 / 12, 0) if amount != 0 else 0
            print(f"{item:.<35} ${amount:>10,.0f} (${per_unit_month}/unit/month)")
    
    # Calculate expense ratio
    total_income = income_data["Total Income"]
    total_expenses = expense_data["Total Operating Expenses"]
    expense_ratio = (total_expenses / total_income) * 100
    
    print()
    print("📈 PERFORMANCE METRICS (T-12 Actual)")
    print("-" * 40)
    print(f"Total Income: ${total_income:,.0f}")
    print(f"Operating Expenses: ${total_expenses:,.0f}")
    print(f"Expense Ratio: {expense_ratio:.1f}%")
    print(f"NOI: ${expense_data['Net Operating Income']:,.0f}")
    print(f"NOI Margin: {(expense_data['Net Operating Income']/total_income)*100:.1f}%")
    
    return {
        "income": income_data,
        "expenses": expense_data,
        "period": "Jun 2024 - May 2025 (12 months actual)",
        "expense_ratio": expense_ratio
    }

if __name__ == "__main__":
    data = extract_t12_actual_data()
    print(f"\n✅ Extracted T-12 data for period: {data['period']}")
    print(f"📊 Expense Ratio: {data['expense_ratio']:.1f}%")