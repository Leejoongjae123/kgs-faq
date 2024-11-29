import json
import pprint
import re
import time
from bs4 import BeautifulSoup
import requests
import datetime
import pprint
import boto3
import os
from dotenv import load_dotenv
import schedule
def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)
def GetSearchGasSafetyFAQ():
  results=[]
  # categoryList=[{
  #   "categoryName":"고압가스",
  #   "categoryCode":"GAS001"  
  # },{
  #   "categoryName":"액화석유가스",
  #   "categoryCode":"GAS002"  
  # },{
  #   "categoryName":"도시가스",
  #   "categoryCode":"GAS003"  
  # },{
  #   "categoryName":"수소",
  #   "categoryCode":"GAS004"  
  # },{
  #   "categoryName":"기타",
  #   "categoryCode":"GAS005"  
  # }
  # ]
  # for category in categoryList:
  pageIndex=1
  endFlag=False
  fileNameList=[]
  while True:

    cookies = {
        'JSESSIONID': '82951E27E7102D916CF4E239480FC6E8.tomcat2',
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        # 'Cookie': 'JSESSIONID=82951E27E7102D916CF4E239480FC6E8.tomcat2',
        'Origin': 'https://www.kgs.or.kr',
        'Referer': 'https://www.kgs.or.kr/kgs/aaaa/board.do',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    data = {
        'pageIndex': pageIndex,
        'etc1': "",
        'searchType': '1',
        'searchText': '',
    }
    while True:
      try:
        response = requests.post('https://www.kgs.or.kr/kgs/aaaa/board.do', cookies=cookies, headers=headers, data=data)
        break
      except:
        print("에러발생")
        time.sleep(1)
    soup=BeautifulSoup(response.text, 'html.parser')
    with open('source/kgs_faq.html', 'w', encoding='utf-8') as outfile:
      outfile.write(response.text)
    items=soup.find_all('section', class_='faq-list')
    print(len(items))
    if len(items)==0:
      print('글없음1')
      break
    for item in items:
      title=item.find('li',class_='text').get_text().strip()
      if title=="내용이 없습니다":
        print('글없음2')
        endFlag=True
        break
      for br in item.find_all('br'):
          br.replace_with('\n')
      contents = item.find('div', class_='faq_con').get_text().strip()
      indexNo=item.find('li',class_='number').get_text().strip()
      regiDate=item.find("li",class_="date").get_text().strip()
      category=item.find('li',class_="sort").get_text().strip()
      result={"title":title,"contents":contents,'category':category,'indexNo':indexNo,'regiDate':regiDate}
      
      with open('source/kgs_faq.json', 'r', encoding='utf-8') as file:
          kgs_faq_data = json.load(file)
      # pprint.pprint(kgs_faq_data)
      # 데이타 형태변환
      regiDate = datetime.datetime.strptime(regiDate, "%Y.%m.%d").strftime("%Y-%m-%d 00:00:00")
      kgs_faq_data['KGS-FAQ'][0]['metadata']['CreationDate'] = regiDate
      kgs_faq_data['KGS-FAQ'][0]['metadata']['ModDate'] = regiDate
      categoryList={
        '고압가스':'GAS001',
        '액화석유가스':'GAS002',
        '도시가스':'GAS003',
        '수소':'GAS004',
        '기타':'GAS005'
      }
      categoryCode = categoryList.get(category, "GAS005")  # Default to "000" if category not found
      kgs_faq_data['KGS-FAQ'][0]['metadata']['Category'] = categoryCode
      
      kgs_faq_data['KGS-FAQ'][0]['data']['title'] = title
      kgs_faq_data['KGS-FAQ'][0]['data']['content']['questionDate'] = regiDate
      kgs_faq_data['KGS-FAQ'][0]['data']['content']['answerDate'] = regiDate
      kgs_faq_data['KGS-FAQ'][0]['data']['id'] = indexNo
      
      def sanitize_filename(filename):
          # 파일명으로 사용할 수 없는 특수문자 리스트
          invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
          
          # 공백은 언더스코어로 변경
          filename = filename.replace(' ', '_')
          
          # 특수문자 제거
          for char in invalid_chars:
              filename = filename.replace(char, '')
          
          # 추가적인 제어문자나 특수문자 제거
          filename = ''.join(char for char in filename if char.isprintable())
          
          # 파일명 길이 제한 (선택사항, S3는 1024바이트까지 지원)
          if len(filename.encode('utf-8')) > 225:  # 여유있게 225바이트로 제한
              filename = filename[:75]  # UTF-8에서 한글은 3바이트이므로 대략적으로 계산
          
          return filename


      sanitized_title = sanitize_filename(title)
      sanitized_category = sanitize_filename(category)
      sanitized_indexNo = sanitize_filename(indexNo)
      
      # Extract question and answer using regex
      question_match = re.search(r'\(질의내용\)(.*?)\(답변내용\)', contents, re.DOTALL)
      answer_match = re.search(r'\(답변내용\)(.*)', contents, re.DOTALL)
      
      if question_match and answer_match:
          question_text = question_match.group(1).strip()
          answer_text = answer_match.group(1).strip()
          
          # Split the text into lists
          questions = [line.strip() for line in question_text.split('\n') if line.strip()]
          answers = [line.strip() for line in answer_text.split('\n') if line.strip()]
      else:
            # Use title as the question and contents as the answer
          questions = [title]
          answers = [line.strip() for line in contents.split('\n') if line.strip()]
      kgs_faq_data['KGS-FAQ'][0]['data']['content']['questions'] = questions
      kgs_faq_data['KGS-FAQ'][0]['data']['content']['answers'] = answers

      file_name = f'result/{sanitized_title}_{sanitized_category}_{sanitized_indexNo}.json'
      fileNameList.append(file_name)
      kgs_faq_data['KGS-FAQ'][0]['metadata']['FileName'] = file_name.replace("result/", "")
      with open(file_name, 'w', encoding='utf-8') as outfile:
          json.dump(kgs_faq_data, outfile, ensure_ascii=False, indent=2)
    if endFlag:
      print("더없음2")
      break
    print("pageIndex:",pageIndex)
    pageIndex+=1
    time.sleep(1)
  return fileNameList

# GetSearchGasSafetyFAQ()
def UploadImageToS3(file_path):
    # AWS 계정의 액세스 키와 시크릿 키를 설정합니다.

    aws_access_key_id=os.getenv('aws_access_key_id')
    aws_secret_access_key=os.getenv('aws_secret_access_key')
    region_name=os.getenv('region_name')
    bucket_name=os.getenv('bucket_name')
    print(aws_access_key_id,aws_secret_access_key,region_name,bucket_name)
    # S3 클라이언트를 생성합니다.
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )
        
    s3_path = file_path.replace('result/', '')

    try:
        response = s3_client.upload_file(
            Filename=file_path,
            Bucket=bucket_name,
            Key=s3_path
        )
        print("파일 업로드 성공!")
    except Exception as e:
        print("파일 업로드 실패:", str(e))
        return None
        
    url = f'https://{bucket_name}.s3.{region_name}.amazonaws.com/{s3_path}'
    print("url:", url, "/ url_TYPE:", type(url))
    return url


def PrintS3FileNames():
    aws_access_key_id = os.getenv('aws_access_key_id')
    aws_secret_access_key = os.getenv('aws_secret_access_key')
    region_name = os.getenv('region_name')
    bucket_name = os.getenv('bucket_name')

    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )

    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            for obj in response['Contents']:
                print(obj['Key'])
        else:
            print("버킷에 파일이 없습니다.")
    except Exception as e:
        print("파일 목록을 가져오는 데 실패했습니다:", str(e))

#환경변수로드
load_dotenv()





def job():
  #폴더생성
  createFolder('source')
  createFolder('result')
  # 데이타 수집
  fileNameList=GetSearchGasSafetyFAQ()
  with open('source/fileNameList.json', 'w', encoding='utf-8') as outfile:
      json.dump(fileNameList, outfile, ensure_ascii=False, indent=2)

  #S3업로드
  hostingUrlList=[]
  for fileName in fileNameList:
    try:
      hostingUrl=UploadImageToS3(fileName)
      hostingUrlList.append(hostingUrl)
    except Exception as e:
      print("업로드 실패:",fileName,"/ 에러:",e)

  with open('source/hostingUrlList.json', 'w', encoding='utf-8') as outfile:
      json.dump(hostingUrlList, outfile, ensure_ascii=False, indent=2)
  


firstFlag=True
# 매일 오전 6시에 job 함수 실행
schedule.every().day.at("06:00").do(job)

while True:
    if firstFlag:
      firstFlag=False
      job()
    print("현재시간:",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    schedule.run_pending()
    time.sleep(60)





