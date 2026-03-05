from flask import Flask, request, jsonify
app = Flask(__name__)
line_bot_api = LineBotApi("YOUR_CHANNEL_ACCESS_TOKEN")
handler = WebhookHandler("YOUR_CHANNEL_SECRET")
def calculate_bmi(weight, height):
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    return round(bmi, 2)
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return 'Invalid signature', 400
    return 'OK'
@app.route("/bmi", methods=["POST"])
def bmi():
    data = request.json
    weight = float(data["weight"])
    height = float(data["height"])
    bmi_value = calculate_bmi(weight, height)
    if bmi_value < 18.5:
        advice = "น้ำหนักน้อย ควรเพิ่มพลังาน เช่น ข้าวมันไก่ต้ม หรือ ข้าวมันไก่ทอด"
    elif bmi_value < 23:
        advice = "ปกติ ควรรักษาสมดุล เช่น ข้าวต้ม"
    else:
        advice = "น้ำหนักเกิน ควรลดของมันและหวาน"
    return jsonify({
        "bmi": bmi_value,
        "advice": advice
    })
import tensorflow as tf
import numpy as np
from PIL import Image
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, ImageMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
model = tf.keras.models.load_model("keras_model.h5")
with open("labels.txt", "r", encoding="utf-8") as f:
    class_names = [line.strip() for line in f.readlines()]
calories_dict = {
    "0 ก๋วยเตี๋ยว": 250,
    "1 ข้าวมันไก่ต้ม": 657,
    "2 ข้าวมันไก่ทอด": 695,
    "3 ข้าวกะเพรา": 580,
    "4 ข้าวต้ม": 228,
}

@app.route("/predict", methods=["POST"])
def predict():
    file = request.files["image"]
    img = Image.open(file).convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    prediction = model.predict(img_array)
    index = np.argmax(prediction)
    predicted_class = class_names[index]
    calories = calories_dict.get(predicted_class, "ไม่พบข้อมูล")
    return jsonify({
        "food": predicted_class,
        "calories": calories
    })
    if __name__ == "__main__":
        app.run(debug=True)
