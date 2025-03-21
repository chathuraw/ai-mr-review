import json

from openai import OpenAI

class AIAnalyzer:
    def __init__(self, api_key: str):
        print("OPEN AI : ", api_key)
        self.client = OpenAI(api_key=api_key)

    def analyze_mr(self, mr_data, mr_diff):
        # Kod farklarını ve MR açıklamasını birleştir
        diff_text = "\n".join([diff["diff"] for diff in mr_diff])
        prompt = (
            f"Senior bir yazılım geliştirici olarak aşağıdaki GitLab Merge Request'ı incele:\n"
            f"MR Başlığı: {mr_data['title']}\n"
            f"Açıklama: {mr_data['description']}\n"
            f"Kod Değişiklikleri:\n```diff\n{diff_text}\n```\n"
            f"Performans, okunabilirlik, hata olasılıkları ve tasarım açısından yorum yap.\n"
            f"Çıktıyı şu formatta JSON olarak döndür:\n"
            f'{{"summary": "özet", "positives": "iyi yönler", "suggestions": "iyileştirme önerileri"}}'
        )

        # OpenAI ile analiz
        response = self.client.chat.completions.create(
            model="gpt-4o",  # Önerilen model, alternatif: "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "Kod analizi yapan bir senior developersın."},
                {"role": "user", "content": prompt}
            ],
        )

        # JSON formatında analiz sonucunu al
        analysis_json = response.choices[0].message.content
        cleaned_analysis_json = analysis_json.strip('`').replace('json\n', '', 1).strip()

        return json.loads(cleaned_analysis_json)