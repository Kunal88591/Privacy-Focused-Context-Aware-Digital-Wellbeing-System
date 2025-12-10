"""
Insights Generator
Advanced insights generation using pattern recognition and ML predictions
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import statistics
from collections import defaultdict


class InsightsGenerator:
    """Generate advanced insights from user analytics data"""
    
    def __init__(self):
        """Initialize insights generator"""
        self.insight_categories = [
            'productivity', 'focus', 'wellbeing', 'habits',
            'screen_time', 'notifications', 'breaks', 'goals'
        ]
    
    # ==================== Pattern Recognition ====================
    
    def identify_peak_hours(self, hourly_data: List[Dict]) -> Dict:
        """Identify user's peak productivity hours"""
        if not hourly_data:
            return {}
        
        # Find hours with highest activity
        sorted_hours = sorted(hourly_data, key=lambda x: x.get('minutes', 0), reverse=True)
        
        peak_hours = sorted_hours[:3]
        low_hours = sorted_hours[-3:]
        
        # Categorize by time of day
        morning = [h for h in hourly_data if 6 <= h['hour'] < 12]
        afternoon = [h for h in hourly_data if 12 <= h['hour'] < 18]
        evening = [h for h in hourly_data if 18 <= h['hour'] < 24]
        
        best_period = max(
            [
                ('morning', sum(h.get('minutes', 0) for h in morning)),
                ('afternoon', sum(h.get('minutes', 0) for h in afternoon)),
                ('evening', sum(h.get('minutes', 0) for h in evening))
            ],
            key=lambda x: x[1]
        )
        
        # Format peak hours for response
        formatted_peak_hours = [{'hour': h['hour'], 'time': h['time_label'], 'minutes': h['minutes']} 
                               for h in peak_hours]
        
        return {
            'peak_hours': formatted_peak_hours,
            'low_activity_hours': [{'hour': h['hour'], 'time': h['time_label']} 
                                  for h in low_hours],
            'best_period': best_period[0],
            'best_period_minutes': best_period[1],
            'recommendation': self._get_peak_hour_recommendation(formatted_peak_hours, best_period[0])
        }
    
    def detect_usage_patterns(self, daily_summaries: List[Dict]) -> Dict:
        """Detect patterns in daily usage"""
        if len(daily_summaries) < 3:
            return {'patterns': [], 'message': 'Need more data to detect patterns'}
        
        patterns = []
        
        # Check for consistent focus time
        focus_times = [d['total_focus_time_minutes'] for d in daily_summaries]
        focus_consistency = self._calculate_consistency(focus_times)
        
        if focus_consistency > 0.8:
            patterns.append({
                'type': 'consistent_focus',
                'strength': 'strong',
                'message': 'You maintain consistent focus time across days',
                'icon': '📊'
            })
        elif focus_consistency < 0.5:
            patterns.append({
                'type': 'inconsistent_focus',
                'strength': 'weak',
                'message': 'Your focus time varies significantly day-to-day',
                'icon': '⚠️'
            })
        
        # Check for weekend vs weekday patterns
        weekday_avg_screen = statistics.mean([
            d['total_screen_time_minutes'] for d in daily_summaries 
            if self._is_weekday(d['date'])
        ]) if any(self._is_weekday(d['date']) for d in daily_summaries) else 0
        
        weekend_avg_screen = statistics.mean([
            d['total_screen_time_minutes'] for d in daily_summaries 
            if not self._is_weekday(d['date'])
        ]) if any(not self._is_weekday(d['date']) for d in daily_summaries) else 0
        
        if weekend_avg_screen > 0 and weekday_avg_screen > 0:
            diff_percent = abs(weekend_avg_screen - weekday_avg_screen) / weekday_avg_screen * 100
            
            if diff_percent > 30:
                patterns.append({
                    'type': 'weekend_difference',
                    'strength': 'strong',
                    'message': f'Weekend screen time differs by {diff_percent:.0f}% from weekdays',
                    'weekday_avg': round(weekday_avg_screen, 1),
                    'weekend_avg': round(weekend_avg_screen, 1),
                    'icon': '📅'
                })
        
        # Check for notification handling patterns
        interaction_rates = [d.get('notification_interaction_rate', 0) for d in daily_summaries]
        avg_interaction = statistics.mean(interaction_rates) if interaction_rates else 0
        
        if avg_interaction > 70:
            patterns.append({
                'type': 'high_notification_engagement',
                'strength': 'strong',
                'message': 'You interact with most notifications - consider filtering',
                'rate': round(avg_interaction, 1),
                'icon': '🔔'
            })
        elif avg_interaction < 30:
            patterns.append({
                'type': 'low_notification_engagement',
                'strength': 'moderate',
                'message': 'You ignore most notifications - good focus discipline!',
                'rate': round(avg_interaction, 1),
                'icon': '🔕'
            })
        
        return {
            'patterns': patterns,
            'pattern_count': len(patterns),
            'analysis_period_days': len(daily_summaries)
        }
    
    def predict_optimal_schedule(self, weekly_data: Dict) -> Dict:
        """Predict optimal daily schedule based on patterns"""
        daily_summaries = weekly_data.get('daily_summaries', [])
        
        if not daily_summaries:
            return {}
        
        # Find best performing day
        best_day = max(daily_summaries, key=lambda x: x['productivity_score'])
        
        # Analyze hourly patterns from all days
        all_hourly = []
        for day in daily_summaries:
            if 'hourly_breakdown' in day:
                all_hourly.extend(day['hourly_breakdown'])
        
        # Aggregate by hour
        hourly_avg = defaultdict(list)
        for h in all_hourly:
            hourly_avg[h['hour']].append(h['minutes'])
        
        hourly_patterns = [
            {
                'hour': hour,
                'avg_minutes': round(statistics.mean(mins), 1),
                'consistency': self._calculate_consistency(mins)
            }
            for hour, mins in hourly_avg.items()
        ]
        
        # Identify optimal blocks
        focus_blocks = self._identify_focus_blocks(hourly_patterns)
        break_times = self._suggest_break_times(hourly_patterns)
        
        return {
            'optimal_focus_blocks': focus_blocks,
            'suggested_break_times': break_times,
            'best_day_analysis': {
                'date': best_day['date'],
                'productivity_score': best_day['productivity_score'],
                'focus_time': best_day['total_focus_time_minutes'],
                'key_factors': self._identify_success_factors(best_day)
            },
            'schedule_recommendations': self._generate_schedule_recommendations(
                focus_blocks, break_times, best_day
            )
        }
    
    def generate_personalized_tips(self, insights_data: Dict, user_patterns: Dict) -> List[Dict]:
        """Generate personalized productivity tips"""
        tips = []
        
        # Based on productivity insights
        if insights_data.get('insights'):
            for insight in insights_data['insights']:
                if insight['type'] == 'warning' and insight['category'] == 'focus':
                    tips.append({
                        'category': 'focus',
                        'tip': 'Try the Pomodoro Technique: 25 minutes focus, 5 minutes break',
                        'priority': 'high',
                        'actionable': True,
                        'icon': '🍅'
                    })
                elif insight['type'] == 'warning' and insight['category'] == 'distractions':
                    tips.append({
                        'category': 'distractions',
                        'tip': 'Block social media apps during your peak focus hours',
                        'priority': 'high',
                        'actionable': True,
                        'icon': '🚫'
                    })
        
        # Based on patterns
        if user_patterns.get('patterns'):
            for pattern in user_patterns['patterns']:
                if pattern['type'] == 'inconsistent_focus':
                    tips.append({
                        'category': 'consistency',
                        'tip': 'Set a recurring calendar event for daily focus time',
                        'priority': 'medium',
                        'actionable': True,
                        'icon': '📅'
                    })
                elif pattern['type'] == 'weekend_difference':
                    tips.append({
                        'category': 'balance',
                        'tip': 'Maintain similar screen time patterns on weekends for better routine',
                        'priority': 'low',
                        'actionable': True,
                        'icon': '⚖️'
                    })
        
        # General wellbeing tips
        tips.extend([
            {
                'category': 'wellbeing',
                'tip': 'Follow the 20-20-20 rule: Every 20 min, look 20 feet away for 20 seconds',
                'priority': 'medium',
                'actionable': False,
                'icon': '👁️'
            },
            {
                'category': 'productivity',
                'tip': 'Plan your most important task for your peak productivity hours',
                'priority': 'high',
                'actionable': True,
                'icon': '🎯'
            }
        ])
        
        return tips
    
    def calculate_wellbeing_score(self, daily_summary: Dict) -> Dict:
        """Calculate comprehensive wellbeing score"""
        # Components (each 0-100)
        
        # 1. Screen time health (lower is better for wellbeing)
        screen_time_hours = daily_summary['total_screen_time_minutes'] / 60
        screen_score = max(0, 100 - (screen_time_hours / 12 * 100))
        
        # 2. Break adherence (more breaks = better wellbeing)
        breaks_count = daily_summary['breaks_count']
        break_score = min(breaks_count * 15, 100)  # Ideal: 6-7 breaks
        
        # 3. Focus quality
        focus_quality = daily_summary.get('average_focus_quality', 50)
        
        # 4. Work-life balance (based on screen time distribution)
        # This would need hourly data
        balance_score = 75  # Placeholder
        
        # 5. Notification stress (fewer notifications = better)
        notifications = daily_summary['notifications_received']
        notification_score = max(0, 100 - (notifications / 100 * 100))
        
        # Weighted average
        wellbeing_score = (
            screen_score * 0.25 +
            break_score * 0.20 +
            focus_quality * 0.20 +
            balance_score * 0.20 +
            notification_score * 0.15
        )
        
        # Determine wellbeing level
        if wellbeing_score >= 80:
            level = 'excellent'
            emoji = '🌟'
        elif wellbeing_score >= 60:
            level = 'good'
            emoji = '😊'
        elif wellbeing_score >= 40:
            level = 'fair'
            emoji = '😐'
        else:
            level = 'needs_attention'
            emoji = '😟'
        
        return {
            'overall_score': round(wellbeing_score, 1),
            'level': level,
            'emoji': emoji,
            'components': {
                'screen_time_health': round(screen_score, 1),
                'break_adherence': round(break_score, 1),
                'focus_quality': round(focus_quality, 1),
                'work_life_balance': round(balance_score, 1),
                'notification_management': round(notification_score, 1)
            },
            'recommendations': self._get_wellbeing_recommendations(
                screen_score, break_score, focus_quality, notification_score
            )
        }
    
    def generate_comparison_report(self, user_data: Dict, benchmark_data: Optional[Dict] = None) -> Dict:
        """Generate comparison report against benchmarks or personal bests"""
        if benchmark_data is None:
            # Use general healthy benchmarks
            benchmark_data = {
                'screen_time_hours': 6,
                'focus_time_minutes': 180,
                'productivity_score': 70,
                'breaks_count': 6,
                'notification_interaction_rate': 40
            }
        
        comparisons = []
        
        # Screen time comparison
        user_screen = user_data.get('total_screen_time_minutes', 0) / 60
        benchmark_screen = benchmark_data.get('screen_time_hours', 6)
        screen_diff = ((user_screen - benchmark_screen) / benchmark_screen * 100) if benchmark_screen > 0 else 0
        
        comparisons.append({
            'metric': 'Screen Time',
            'user_value': f"{user_screen:.1f} hours",
            'benchmark_value': f"{benchmark_screen:.1f} hours",
            'difference_percent': round(screen_diff, 1),
            'status': 'better' if screen_diff < 0 else 'worse',
            'icon': '📱'
        })
        
        # Focus time comparison
        user_focus = user_data.get('total_focus_time_minutes', 0)
        benchmark_focus = benchmark_data.get('focus_time_minutes', 180)
        focus_diff = ((user_focus - benchmark_focus) / benchmark_focus * 100) if benchmark_focus > 0 else 0
        
        comparisons.append({
            'metric': 'Focus Time',
            'user_value': f"{user_focus:.0f} minutes",
            'benchmark_value': f"{benchmark_focus:.0f} minutes",
            'difference_percent': round(focus_diff, 1),
            'status': 'better' if focus_diff > 0 else 'worse',
            'icon': '🎯'
        })
        
        # Productivity score comparison
        user_productivity = user_data.get('productivity_score', 0)
        benchmark_productivity = benchmark_data.get('productivity_score', 70)
        prod_diff = user_productivity - benchmark_productivity
        
        comparisons.append({
            'metric': 'Productivity Score',
            'user_value': f"{user_productivity:.0f}/100",
            'benchmark_value': f"{benchmark_productivity:.0f}/100",
            'difference_points': round(prod_diff, 1),
            'status': 'better' if prod_diff > 0 else 'worse',
            'icon': '📊'
        })
        
        # Overall assessment
        better_count = sum(1 for c in comparisons if c['status'] == 'better')
        overall_status = 'exceeding' if better_count >= 2 else 'below' if better_count == 0 else 'meeting'
        
        return {
            'overall_status': overall_status,
            'metrics_better': better_count,
            'metrics_worse': len(comparisons) - better_count,
            'comparisons': comparisons,
            'summary': f"You are {overall_status} healthy benchmarks in {better_count} out of {len(comparisons)} metrics"
        }
    
    # ==================== Helper Methods ====================
    
    def _calculate_consistency(self, values: List[float]) -> float:
        """Calculate consistency score (0-1) based on coefficient of variation"""
        if not values or len(values) < 2:
            return 0
        
        mean_val = statistics.mean(values)
        if mean_val == 0:
            return 0
        
        std_dev = statistics.stdev(values)
        cv = std_dev / mean_val
        
        # Convert CV to consistency score (lower CV = higher consistency)
        consistency = max(0, 1 - (cv / 2))
        return consistency
    
    def _is_weekday(self, date_str: str) -> bool:
        """Check if date is a weekday"""
        date = datetime.fromisoformat(date_str)
        return date.weekday() < 5  # Monday = 0, Friday = 4
    
    def _get_peak_hour_recommendation(self, peak_hours: List[Dict], best_period: str) -> str:
        """Get recommendation based on peak hours"""
        peak_times = [h['time'] for h in peak_hours]
        return f"Schedule important tasks during your peak hours: {', '.join(peak_times)}. Your {best_period} is most productive."
    
    def _identify_focus_blocks(self, hourly_patterns: List[Dict]) -> List[Dict]:
        """Identify optimal 2-hour focus blocks"""
        sorted_hours = sorted(hourly_patterns, key=lambda x: x['avg_minutes'], reverse=True)
        
        focus_blocks = []
        for i in range(min(3, len(sorted_hours) - 1)):
            hour = sorted_hours[i]['hour']
            focus_blocks.append({
                'start_time': f"{hour:02d}:00",
                'end_time': f"{(hour + 2) % 24:02d}:00",
                'avg_activity': sorted_hours[i]['avg_minutes'],
                'consistency': sorted_hours[i]['consistency']
            })
        
        return focus_blocks
    
    def _suggest_break_times(self, hourly_patterns: List[Dict]) -> List[str]:
        """Suggest optimal break times"""
        # Suggest breaks after high-activity periods
        sorted_hours = sorted(hourly_patterns, key=lambda x: x['avg_minutes'], reverse=True)
        
        break_times = []
        for pattern in sorted_hours[:3]:
            break_hour = (pattern['hour'] + 1) % 24
            break_times.append(f"{break_hour:02d}:00")
        
        return break_times
    
    def _identify_success_factors(self, best_day: Dict) -> List[str]:
        """Identify factors that made a day successful"""
        factors = []
        
        if best_day['total_focus_time_minutes'] > 180:
            factors.append('Extended focus sessions')
        
        if best_day['distractions_count'] < 10:
            factors.append('Low distractions')
        
        if best_day['breaks_count'] >= 4:
            factors.append('Regular breaks')
        
        if best_day.get('average_focus_quality', 0) > 70:
            factors.append('High focus quality')
        
        return factors if factors else ['Balanced productivity']
    
    def _generate_schedule_recommendations(self, focus_blocks: List[Dict], 
                                          break_times: List[str], best_day: Dict) -> List[str]:
        """Generate actionable schedule recommendations"""
        recommendations = []
        
        if focus_blocks:
            first_block = focus_blocks[0]
            recommendations.append(
                f"Block {first_block['start_time']}-{first_block['end_time']} for deep work"
            )
        
        if len(break_times) > 0:
            recommendations.append(f"Take breaks around {', '.join(break_times[:2])}")
        
        recommendations.append(
            f"Replicate conditions from {best_day['date']} - your best day"
        )
        
        return recommendations
    
    def _get_wellbeing_recommendations(self, screen_score: float, break_score: float,
                                      focus_quality: float, notification_score: float) -> List[str]:
        """Get recommendations to improve wellbeing"""
        recommendations = []
        
        if screen_score < 50:
            recommendations.append('Reduce total screen time - aim for max 8 hours/day')
        
        if break_score < 50:
            recommendations.append('Take more frequent breaks - target 1 every 90 minutes')
        
        if focus_quality < 60:
            recommendations.append('Improve focus environment - minimize distractions')
        
        if notification_score < 50:
            recommendations.append('Reduce notification frequency - batch check instead')
        
        if not recommendations:
            recommendations.append('Great job! Maintain your current wellbeing habits')
        
        return recommendations


# Global insights generator instance
insights_generator = InsightsGenerator()
