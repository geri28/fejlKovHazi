import cv2
import math
import numpy as np
import matplotlib.pyplot as plt
import os

folder_path = "./ora"
extensions = ("jpg", "jpeg", "webp", "png")

images = [
    f for f in os.listdir(folder_path)
    if f.lower().endswith(extensions) and os.path.isfile(os.path.join(folder_path, f))
]

print(images)

def plot_images(images, titles=None, cols=2, figsize=(10, 6), cmap=None):
    if isinstance(images, dict):
        titles = list(images.keys())
        images = list(images.values())
    elif titles is None:
        titles = [f"Image {i}" for i in range(len(images))]

    rows = (len(images) + cols - 1) // cols
    plt.figure(figsize=figsize)

    for i, (img, title) in enumerate(zip(images, titles)):
        plt.subplot(rows, cols, i + 1)
        if len(img.shape) == 2 or cmap:
            plt.imshow(img, cmap=cmap or 'gray')
        else:
            plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))  # BGR to RGB
        plt.title(title)
        plt.axis('off')

    plt.tight_layout()
    plt.show()

SCALAR_MIDDLE_INTERSECTION = 0.2
SCALAR_OUTERLINE = 0.65
IMAGEDICTIONARY = {}
# OK:1,3,4, 8,9, 10, 11, 13
# 0, 2 (mutató egyszinű háttérrel), 5 (perc mutató szín miatt eltünik),6 (szinte jó csak mintákbezavarnak),7 (szinek bezavarnak) 12 (nem találja a középpontot), 14(saját kép a minták bezavarnak)
getImage = images[15]
original_image = cv2.imread(f"./ora/{getImage}")
image = original_image.copy()


modified_image = image.copy()
handles_image = image.copy()

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.medianBlur(gray, 5)  
bilateralFilter = cv2.bilateralFilter(blurred, 7, sigmaColor=50, sigmaSpace=75)
_, thresh = cv2.threshold(bilateralFilter, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
edges = cv2.Canny(thresh, 50, 150)  

# plt.imshow(thresh, cmap="gray")
# plt.title("asd")
# plt.axis("off")
# plt.show()

circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.2, 100)
for circle in circles:
    x, y = [int(val) for val in circle[0][:2]]
    r = int(circle[0][2])
    cv2.circle(image, (x,y), r, (255, 0, 0), 5)
center = 0
r = 0
if circles is not None:
    circles = np.round(circles[0, :]).astype("int")
    # Sort circles by radius and pick the smallest
    # smallest_circle = sorted(circles, key=lambda c: c[2])[-1]
    # cx, cy, r = smallest_circle
    # approx_center = (cx, cy)
    # cv2.circle(image, approx_center, r, (0, 255, 255), 3)
    
    # Kép közepe
    image_center = (gray.shape[1] // 2, gray.shape[0] // 2)

    closest_circle = min(circles, key=lambda c: np.hypot(c[0] - image_center[0], c[1] - image_center[1]))
    cx, cy, r = map(int, closest_circle)
    approx_center = (cx, cy)
    cv2.circle(image, approx_center, r, (0, 255, 255), 3)


    # ---- ÚJ: pontosítás kontúrok alapján ----
    closest_center = approx_center
    min_distance = float('inf')

    cx, cy = closest_center
    center = (cx, cy)
    print(f"🟢 Finomított középpont: {center} (Hough-kör alapján: {approx_center})")

    cv2.circle(image, center, 3, (255, 0, 0), -1)

x, y = center

# eredti kép méretéről maszkolás
mask = np.zeros_like(thresh)
cv2.circle(mask, (x, y), r, 255, thickness=-1)

masked_image = cv2.bitwise_and(thresh, thresh, mask=mask)
cv2.circle(masked_image, (x, y), int(r-3), (255, 255, 255), 10)


# Threshold the masked image to get binary image for contour detection
_, thresh = cv2.threshold(masked_image, 100, 200, cv2.THRESH_BINARY + cv2.THRESH_OTSU)


cv2.circle(thresh, (x, y), int(r*SCALAR_OUTERLINE), (255, 255, 255), 5)
cv2.circle(thresh, (x, y), int(r*SCALAR_MIDDLE_INTERSECTION), (255, 255, 255), -1)


contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

center_x, center_y = center
cv2.circle(image, (x, y), 3, (255, 0, 0), -1)
contour_candidates = []

for cnt in contours:
    M = cv2.moments(cnt)
    if M["m00"] == 0:
        continue
    cx_cnt = int(M["m10"] / M["m00"])
    cy_cnt = int(M["m01"] / M["m00"])
    
    # Compute distance to center
    dist = np.hypot(cx_cnt - center_x, cy_cnt - center_y)
    contour_candidates.append((dist, cnt, (cx_cnt, cy_cnt)))

# óra közepe által rendezés
contour_candidates.sort(key=lambda x: x[0])

N = 10  # how many closest to consider
closest_candidates = contour_candidates[:N]

# Compute area and sort by size descending
closest_largest = sorted(
    [
        (cv2.contourArea(cnt), cnt, centroid)
        for _, cnt, centroid in closest_candidates
        if (
            cv2.contourArea(cnt) < math.pi * (r * SCALAR_OUTERLINE) ** 2 and
            np.hypot(centroid[0] - center_x, centroid[1] - center_y) < r * SCALAR_OUTERLINE
        )
    ],
    key=lambda x: x[0],
    reverse=True
)

top2_contours = closest_largest[:2]

# Draw them
for i, (area, cnt, centroid) in enumerate(top2_contours):
    color = (0, 255, 0) if i == 0 else (0, 0, 255)  # Green and Red
    cv2.drawContours(modified_image, [cnt], -1, color, 2)
    cv2.circle(modified_image, centroid, 5, color, -1)
    cv2.putText(modified_image, f"N{i+1} A:{int(area)}", (centroid[0]+15, centroid[1]-15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
    

# Analyze top 2 by area and classify
hand_data = []
for area, cnt, centroid in top2_contours:
    length = math.hypot(centroid[0] - x, centroid[1] - y)

    # Vastagság becslés: kontúr bounding box alapján
    rect = cv2.minAreaRect(cnt)
    (_, _), (w, h), _ = rect
    thickness = min(w, h)

    hand_data.append({
        "area": area,
        "cnt": cnt,
        "centroid": centroid,
        "length": length,
        "thickness": thickness
    })

hand_data_sorted = sorted(hand_data, key=lambda h: h['length'], reverse=True)

if abs(hand_data_sorted[0]['length'] - hand_data_sorted[1]['length']) < hand_data_sorted[0]['length'] * 0.1:
    print("Hasonló hosszú mutatók — vastagság alapján választunk")
    if hand_data_sorted[0]['thickness'] > hand_data_sorted[1]['thickness']:
        minute_hand = hand_data_sorted[1]
        hour_hand = hand_data_sorted[0]
    else:
        minute_hand = hand_data_sorted[0]
        hour_hand = hand_data_sorted[1]
else:
    minute_hand = hand_data_sorted[0]
    hour_hand = hand_data_sorted[1]

def calculate_angle(center, point):
    dx = point[0] - center[0]
    dy = center[1] - point[1]  # Flip Y because image origin is top-left
    angle_rad = math.atan2(dy, dx)
    angle_deg = math.degrees(angle_rad)
    angle_clockwise = (90 - angle_deg) % 360 
    return angle_clockwise

# Get angles
minute_angle = calculate_angle(center, minute_hand["centroid"])
hour_angle = calculate_angle(center, hour_hand["centroid"])

minute_value = int(round(minute_angle / 6)) % 60
if(minute_value == 0):
    hour_value = int(((hour_angle / 30)) % 12)+1
else:
    hour_value = int((hour_angle / 30)) % 12
# Adjust hour with minute overlap
hour_value = (hour_value + (minute_value / 60)) % 12


cv2.drawContours(handles_image, [minute_hand["cnt"]], -1, (0, 255, 0), 2)  # Green
cv2.putText(handles_image, f"Minute: {int(minute_value)}", (minute_hand["centroid"][0] + 15, minute_hand["centroid"][1] - 15),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1)

cv2.drawContours(handles_image, [hour_hand["cnt"]], -1, (255, 0, 0), 2)  # Blue
cv2.putText(handles_image, f"Hour: {int(hour_value)}", (hour_hand["centroid"][0] + 15, hour_hand["centroid"][1] - 15),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 1)

# Optional debug output
print(f"Hand-selection by Area:")
print(f"Hour hand   -  Area: {hour_hand['area']}, Angle: {int(hour_angle)}")
print(f"Minute hand -  Area: {minute_hand['area']}, Angle: {int(minute_angle)}")

print(f"Estimated time: {int(hour_value):02d}:{minute_value:02d}")


        
IMAGEDICTIONARY = {
    "original": image,
    "contours_closest": modified_image,
    "edges": thresh,
    "mask": thresh,
    "handles": handles_image
}

plot_images(IMAGEDICTIONARY, titles=None, cols=2, figsize=(20,20))