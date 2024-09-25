# def checkSpaces(img, imgThres):
#     global space_counter, free_spaces, reserved_spaces
#     global daily_total_parked_vehicles, daily_reserved_vehicles
    
#     spaces = 0
#     reserved_spaces = 0
#     for i, pos in enumerate(posList):
#         # Ensure default values if not enough elements in pos
#         if len(pos) < 6:
#             print(f"Warning: Unexpected format for position {i}: {pos}")
#             continue  # Skip this entry as it's not in the expected format

#         x, y, reserved, shape, points, size = pos[:6]  # Unpack the first 6 elements safely

#         # Ensure the additional fields have default values if missing
#         was_reserved = pos[6] if len(pos) > 6 else False
#         was_occupied = pos[7] if len(pos) > 7 else False

#         w, h = size

#         # Determine the number of non-zero pixels in the defined shape
#         if shape == 'rect':
#             imgCrop = imgThres[y:y + h, x:x + w]
#             count = cv2.countNonZero(imgCrop)
#         elif shape == 'portrait':
#             imgCrop = imgThres[y:y + h, x:x + w]
#             count = cv2.countNonZero(imgCrop)
#         else:  # 'poly'
#             mask = np.zeros(imgThres.shape, dtype=np.uint8)
#             points_np = np.array(points, dtype=np.int32)
#             cv2.fillPoly(mask, [points_np], 255)
#             imgCrop = cv2.bitwise_and(imgThres, mask)
#             count = cv2.countNonZero(imgCrop)

#         # Check if space is reserved or parked
#         if reserved:
#             color = (0, 255, 255)  # Yellow for reserved
#             thickness = 5
#             if not was_reserved:  # Increment only when transitioning from non-reserved to reserved
#                 daily_reserved_vehicles += 1
#                 posList[i] = (*pos[:6], True, was_occupied)  # Update state in posList
#             reserved_spaces += 1  # Count for displaying purposes
#         elif count < 900:
#             color = (0, 200, 0)  # Green for free space
#             thickness = 5
#             if not was_occupied:  # Increment only when transitioning from not occupied to occupied
#                 daily_total_parked_vehicles += 1
#                 posList[i] = (*pos[:6], was_reserved, True)  # Update state in posList
#             spaces += 1  # Count for displaying purposes
#         else:
#             color = (0, 0, 200)  # Red for occupied
#             thickness = 2
#             # Reset if previously reserved or occupied
#             if was_reserved or was_occupied:
#                 posList[i] = (*pos[:6], False, False)  # Reset states to False

#         # Draw shapes and text with background
#         if shape == 'rect':
#             cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)
#             cv2.putText(img, f'Space {i+1}', (x + 10, y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)
#         elif shape == 'portrait':
#             cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)
#             cv2.putText(img, f'Space {i+1}', (x + 10, y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)
#         else:  # 'poly'
#             if points:
#                 points_np = np.array(points, dtype=np.int32)
#                 cv2.polylines(img, [points_np], isClosed=True, color=color, thickness=thickness)
#                 if points[0]:
#                     cv2.putText(img, f'Space {i+1}', (points[0][0] + 10, points[0][1] + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)
#                     cv2.putText(img, str(count), (points[0][0], points[0][1] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)

#     # Update global counters
#     free_spaces = spaces
#     reserved_spaces = reserved_spaces

#     # Display counters
#     cv2.putText(img, f'Free: {spaces}/{len(posList)}', (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 0), 1, lineType=cv2.LINE_AA)
#     cv2.putText(img, f'Reserved: {reserved_spaces}', (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, lineType=cv2.LINE_AA)
