LEVELS = [
    # (min_points, level_num, title, max_points)
    (0, 1, 'New Voice', 99),
    (100, 2, 'Contributor', 299),
    (300, 3, 'Active Member', 599),
    (600, 4, 'Trusted Respondent', 999),
    (1000, 5, 'Community Champion', None),
]

def get_level_info(total_points):
    for min_pts, level, title, max_pts in LEVELS:
        if max_pts is None or total_points <= max_pts:
            if max_pts:
                span = max_pts - min_pts + 1
                progress = int(((total_points - min_pts) / span) * 100)
                needed = max_pts + 1 - total_points
                nxt = LEVELS[level][2]
            else:
                progress = 100
                needed = 0
                nxt = None
            return {
                'level': level,
                'title': title,
                'points': total_points,
                'progress': max(0, min(100, progress)),
                'next_title': nxt,
                'points_needed': needed,
            }
    # Fallback
    return {'level': 1, 'title': 'New Voice', 'points': total_points,
            'progress': 0, 'next_title': 'Contributor', 'points_needed': 100}