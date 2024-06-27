from openai import OpenAI

client = OpenAI()




response = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {
      "role": "user",
      "content": [
        {"role": "system", "content": "你是一名天使投資人. 現任多家公司總裁. 從一位成功的企業家，化身成極具影響力的網路意見領袖和創業導師，為許多人排憂解惑，成為許多人口中的「師傅」，至今已輔導超過500家公司、和100,000多位專業人士。你精通文案撰寫、銷售、網路行銷等非常多快速賺錢的技能與觀念"},
        {"type": "text", "text":"你需要使用文案技巧根據下面文章重新撰寫 750 字的文章，文章需要包含標題，這個標題要是非常吸引人，並將750字的內容分為子標題，會包含多個主標題"},

        {"type": "text", "text": "What’s in this image?"},
        {
          "type": "image_url",
          "image_url": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
          },
        },
      ],
    }
  ],
  max_tokens=20,
)

print(response.choices[0])