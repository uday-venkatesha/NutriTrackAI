import logging
from typing import List, Dict, Any
from datetime import date, timedelta
from src.database.operations import get_daily_entries, get_user_metrics

logger = logging.getLogger(__name__)

def analyze_daily_nutrition(entries: List[Dict]) -> str:
    """
    Analyze nutrition data for a collection of food entries.
    
    Args:
        entries (List[Dict]): List of food entries with nutrition data
        
    Returns:
        str: A formatted report of the nutrition analysis
    """
    if not entries:
        return "No food entries found for analysis."
    
    # Extract the date from the first entry
    entry_date = date.fromisoformat(entries[0]['date'])
    
    # Calculate total nutrition values
    totals = {
        'calories': 0,
        'protein': 0,
        'carbohydrates': 0,
        'fat': 0,
        'fiber': 0,
        'sugar': 0,
        'sodium': 0
    }
    
    items_by_meal = {}
    unknown_values = False
    
    for entry in entries:
        nutrition = entry['nutrition_data']
        
        # Add to totals
        for key in totals.keys():
            if key in nutrition and nutrition[key] is not None:
                totals[key] += float(nutrition[key])
            else:
                unknown_values = True
        
        # Group by meal time (based on timestamp)
        hour = entry['timestamp'].hour
        if hour < 10:
            meal = "Breakfast"
        elif hour < 14:
            meal = "Lunch"
        elif hour < 18:
            meal = "Snacks"
        else:
            meal = "Dinner"
            
        if meal not in items_by_meal:
            items_by_meal[meal] = []
            
        items_by_meal[meal].append(entry['food_item'])
    
    # Get user metrics if available
    user_metrics = get_user_metrics(entry_date)
    
    # Build the report
    report = [f"Nutrition Analysis for {entry_date.strftime('%A, %B %d, %Y')}"]
    report.append("\n=== Summary ===")
    
    # Add calorie goal comparison if available
    calories_goal = user_metrics.get('calories_goal')
    if calories_goal:
        report.append(f"Total Calories: {totals['calories']:.0f} / {calories_goal} goal")
        if totals['calories'] > calories_goal:
            excess = totals['calories'] - calories_goal
            report.append(f"  ⚠️ {excess:.0f} calories over your daily goal")
        else:
            remaining = calories_goal - totals['calories']
            report.append(f"  ✅ {remaining:.0f} calories remaining for today")
    else:
        report.append(f"Total Calories: {totals['calories']:.0f}")
    
    # Add macro breakdown
    report.append("\n=== Macronutrients ===")
    report.append(f"Protein: {totals['protein']:.1f}g")
    report.append(f"Carbohydrates: {totals['carbohydrates']:.1f}g")
    report.append(f"Fat: {totals['fat']:.1f}g")
    report.append(f"Fiber: {totals['fiber']:.1f}g")
    report.append(f"Sugar: {totals['sugar']:.1f}g")
    report.append(f"Sodium: {totals['sodium']:.0f}mg")
    
    # Calculate macronutrient percentages
    total_calories_from_macros = (
        totals['protein'] * 4 + 
        totals['carbohydrates'] * 4 + 
        totals['fat'] * 9
    )
    
    if total_calories_from_macros > 0:
        protein_percent = (totals['protein'] * 4 / total_calories_from_macros) * 100
        carb_percent = (totals['carbohydrates'] * 4 / total_calories_from_macros) * 100
        fat_percent = (totals['fat'] * 9 / total_calories_from_macros) * 100
        
        report.append(f"\nMacro Ratio: {protein_percent:.0f}% Protein / {carb_percent:.0f}% Carbs / {fat_percent:.0f}% Fat")
    
    # Add meals breakdown
    report.append("\n=== Meals ===")
    for meal, items in items_by_meal.items():
        report.append(f"{meal}: {', '.join(items)}")
    
    # Add disclaimer if needed
    if unknown_values:
        report.append("\nNote: Some nutrition values were unavailable and are not included in the totals.")
    
    return "\n".join(report)

def get_weekly_trend(end_date: date = None) -> str:
    """
    Generate a weekly trend report for the past 7 days.
    
    Args:
        end_date (date, optional): The end date for the report. Defaults to today.
        
    Returns:
        str: A formatted report of weekly nutrition trends
    """
    if end_date is None:
        end_date = date.today()
        
    start_date = end_date - timedelta(days=6)  # 7 days including end_date
    
    report = [f"Weekly Nutrition Trend ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d')})"]
    report.append("=" * 40)
    
    daily_calories = []
    daily_protein = []
    
    # Get data for each day
    current_date = start_date
    while current_date <= end_date:
        entries = get_daily_entries(current_date)
        
        # Calculate totals
        day_calories = sum(entry['nutrition_data'].get('calories', 0) or 0 for entry in entries)
        day_protein = sum(entry['nutrition_data'].get('protein', 0) or 0 for entry in entries)
        
        daily_calories.append(day_calories)
        daily_protein.append(day_protein)
        
        day_name = current_date.strftime("%a")
        report.append(f"{day_name}: {day_calories:.0f} calories, {day_protein:.1f}g protein")
        
        current_date += timedelta(days=1)
    
    # Calculate averages
    if daily_calories:
        avg_calories = sum(daily_calories) / len(daily_calories)
        avg_protein = sum(daily_protein) / len(daily_protein)
        
        report.append("\nWeekly Averages:")
        report.append(f"Calories: {avg_calories:.0f} per day")
        report.append(f"Protein: {avg_protein:.1f}g per day")
        
        # Add weekly insights
        if len(daily_calories) >= 7:
            # Check for trends
            calories_trend = daily_calories[-1] - daily_calories[0]
            if abs(calories_trend) > 200:
                trend_direction = "increasing" if calories_trend > 0 else "decreasing"
                report.append(f"\nYour calorie intake is {trend_direction} through the week.")
            
            # Check consistency
            max_cal = max(daily_calories)
            min_cal = min(daily_calories)
            if max_cal - min_cal > 500:
                report.append("\nYour calorie intake varies significantly between days.")
            else:
                report.append("\nYour calorie intake is consistent throughout the week.")
    
    return "\n".join(report)