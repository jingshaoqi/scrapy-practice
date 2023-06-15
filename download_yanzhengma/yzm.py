import ddddocr


def recognize():
  ocr = ddddocr.DdddOcr()
  with open('./img/00H1_16589210366768982.png', 'rb') as f:
      img_bytes = f.read()
      res = ocr.classification(img_bytes)
      print(res)

recognize()