import datetime
import json
import time
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import boto3
from urllib.parse import urljoin, parse_qs
import os
import glob
import schedule

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory. ' + directory)
def extract_download_url(base_url, javascript_code):
    # 필요한 정보 추출
    if "$.download" not in javascript_code:
        raise ValueError("Invalid javascript code format")
    
    # 파싱: $.download의 첫 번째, 두 번째 파라미터 추출
    parts = javascript_code.split("download(")[1].strip("');").split(",")
    path = parts[0].strip("'\"")
    query_params = parts[1].strip("'\"")
    
    # full URL 생성
    full_url = urljoin(base_url, path) + "?" + query_params
    return full_url
def categorize_code(category):
    if "고압가스" in category:
        return "KGSCode001"
    elif "액화석유가스" in category:
        return "KGSCode002"
    elif "도시가스" in category or "수소" in category:
        return "KGSCode003"
    elif "공통" in category:
        return "KGSCode005"
    else:
        return "UnknownCategory"

def download_file(url, save_path):
    cookies = {
        'WMONID': 'm300laClJYh',
        'cyberJSESSIONID': 'urGMsORUy_HTDY3oTDpZmrYAGVvmvfOvZ5f4E9esLWoGVRfrRI5M!313933250!835582491',
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        # 'Cookie': 'WMONID=m300laClJYh; cyberJSESSIONID=urGMsORUy_HTDY3oTDpZmrYAGVvmvfOvZ5f4E9esLWoGVRfrRI5M!313933250!835582491',
        'Referer': 'https://cyber.kgs.or.kr/kgscode.codeSearch.listV2.ex.do?pubEng2=N&pageIndex=1&pblcRlmCd=&pblcMdclCd=&pblcNm=&pblcCd=&stDayY=2008&stDayM=01&etDayY=2024&etDayM=12&orderKey=stDay&pubEnd01=F',
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
    try:
        response = requests.get(url,cookies=cookies,headers=headers,stream=True)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        print(f"파일 다운로드 성공: {save_path}")
        return True
    except Exception as e:
        print(f"파일 다운로드 실패: {str(e)}")
        return False
def download_file_post(url, save_path):
    cookies = {
        'WMONID': 'm300laClJYh',
        'cyberJSESSIONID': 'urGMsORUy_HTDY3oTDpZmrYAGVvmvfOvZ5f4E9esLWoGVRfrRI5M!313933250!835582491',
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        # 'Cookie': 'WMONID=m300laClJYh; cyberJSESSIONID=urGMsORUy_HTDY3oTDpZmrYAGVvmvfOvZ5f4E9esLWoGVRfrRI5M!313933250!835582491',
        'Referer': 'https://cyber.kgs.or.kr/kgscode.codeSearch.listV2.ex.do?pubEng2=N&pageIndex=1&pblcRlmCd=&pblcMdclCd=&pblcNm=&pblcCd=&stDayY=2008&stDayM=01&etDayY=2024&etDayM=12&orderKey=stDay&pubEnd01=F',
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
    try:
        response = requests.post(url,cookies=cookies,headers=headers,stream=True)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        print(f"파일 다운로드 성공: {save_path}")
        return True
    except Exception as e:
        print(f"파일 다운로드 실패: {str(e)}")
        return False
def GetSearch():
  urlList=[]
  pageIndex=1
  while True:
    cookies = {
        'WMONID': 'm300laClJYh',
        'cyberJSESSIONID': 'urGMsORUy_HTDY3oTDpZmrYAGVvmvfOvZ5f4E9esLWoGVRfrRI5M!313933250!835582491',
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        # 'Cookie': 'WMONID=m300laClJYh; cyberJSESSIONID=urGMsORUy_HTDY3oTDpZmrYAGVvmvfOvZ5f4E9esLWoGVRfrRI5M!313933250!835582491',
        'Referer': 'https://cyber.kgs.or.kr/kgscode.codeSearch.listV2.ex.do?pubEng2=N&pageIndex=1&pblcRlmCd=&pblcMdclCd=&pblcNm=&pblcCd=&stDayY=2008&stDayM=01&etDayY=2024&etDayM=12&orderKey=stDay&pubEnd01=F',
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

    params = {
        'pubEng2': 'N',
        'pageIndex': str(pageIndex),
        'pblcRlmCd': '',
        'pblcMdclCd': '',
        'pblcNm': '',
        'pblcCd': '',
        'stDayY': '2008',
        'stDayM': '01',
        'etDayY': '2024',
        'etDayM': '12',
        'orderKey': 'stDay',
        'pubEnd01': 'F',
    }

    response = requests.get(
        'https://cyber.kgs.or.kr/kgscode.codeSearch.listV2.ex.do',
        params=params,
        cookies=cookies,
        headers=headers,
    )
    soup=BeautifulSoup(response.text, 'html.parser')
    table=soup.find('div',class_="tbl_list01")
    items=table.find_all("a")
    
    if len(items)==0:
      break
    for index,item in enumerate(items):
      itemUrl = item["href"]
      if itemUrl.startswith('/kgscode'):
        urlList.append({'url':"https://cyber.kgs.or.kr"+itemUrl})
    print("갯수는:",len(urlList))
    with open("urlList.json", "w") as file:
      json.dump(urlList, file, ensure_ascii=False, indent=2)
    print("페이지는:",pageIndex)
    pageIndex+=1
    
    time.sleep(1)
def GetDetail(item,infobase):
  cookies = {
      'WMONID': 'm300laClJYh',
      'cyberJSESSIONID': 'urGMsORUy_HTDY3oTDpZmrYAGVvmvfOvZ5f4E9esLWoGVRfrRI5M!313933250!835582491',
  }

  headers = {
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
      'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
      'Cache-Control': 'max-age=0',
      'Connection': 'keep-alive',
      # 'Cookie': 'WMONID=m300laClJYh; cyberJSESSIONID=urGMsORUy_HTDY3oTDpZmrYAGVvmvfOvZ5f4E9esLWoGVRfrRI5M!313933250!835582491',
      'Referer': 'https://cyber.kgs.or.kr/kgscode.codeSearch.listV2.ex.do?pubEng2=N&pageIndex=19&pblcRlmCd=&pblcMdclCd=&pblcNm=&pblcCd=&stDayY=2008&stDayM=01&etDayY=2024&etDayM=12&orderKey=stDay&pubEnd01=F',
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

  response = requests.get(item['url'], cookies=cookies, headers=headers)
  soup=BeautifulSoup(response.text, 'html.parser')
  
  tablePre=soup.find("div",class_="code_tb")
  table=tablePre.find("table")
  tds=table.find_all("td")
  for index,td in enumerate(tds):
    info=td.get_text().strip()
    print("index:",index,"info:",info)
    if index==5:
      CreationDate=info
    if index==4:
      ModDate=info
    if index==1:
      Category=info
    if index==0:
      codeNumber=info
    if index==2:
      koreanTitle=info.replace("\t","").replace("\r","").replace("\n","")
    if index==3:
      englishTitle=info.replace("\t","").replace("\r","").replace("\n","")
    if index==7:
      status=info
    if index==6:
      comparisonFile_fileName=info
      comparisonFile_fileUrl="\\kgs-code\\attachments\\{}".format(datetime.datetime.now().strftime("%Y%m"))
      downloadUrl = "https://cyber.kgs.or.kr" + td.find('a')['href']
      print("downloadUrl:",downloadUrl)
      download_file(downloadUrl, "result/{}".format(comparisonFile_fileName))
  print("codeNumber:",codeNumber)
  print("koreanTitle:",koreanTitle)
  print("englishTitle:",englishTitle)
  print("ModDate:",ModDate)
  print("Category:",Category)
  category_code = categorize_code(Category)
  print("category_code:", category_code)
  print("CreationDate:",CreationDate)
  print("status:",status)
  print("comparisonFile_fileName:",comparisonFile_fileName)
  FileName="{}_{}_{}.JSON".format(codeNumber, koreanTitle, ModDate.replace(".", "")[:8])
  print("FileName:",FileName)
  revision_history=[]
  revisionTable=soup.find("div",class_="tbl_list01").find('tbody')
  trs=revisionTable.find_all("tr")
  for index,tr in enumerate(trs):
    # print('tr:',tr)
    for index2,td in enumerate(tr.find_all("td")):
      info=td.get_text().strip()
      # print("index:",index,"index2:",index2,"info:",info)
      if index2==1:
        revisionType=info
      if index2==0:
        revisionDate=info
      if index2==2:
        codeVersion=info      
      if index2==3:
        fileUrl="\\kgs-code\\attachments\\{}".format(datetime.datetime.now().strftime("%Y%m"))
        revisionReasonFile=info
        if len(revisionReasonFile)>0:
          
          try:
            revisionReasonFileUrl="https://cyber.kgs.or.kr"+td.find('a')['href']
            download_file(revisionReasonFileUrl, "result/{}".format(revisionReasonFile))
            print("파일있음")
          except:
            print("파일없음")          
        else:
          print("파일없음")
      if index2 ==4:
        eBookFile = td.find('a')['href'].split('file_nm=')[1].split('&')[0].replace("/","")
        base_url = "https://cyber.kgs.or.kr"
        if len(eBookFile)>0:
          
          try:
            download_url = extract_download_url(base_url, td.find('a')['href'])
            download_file_post(download_url, "result/{}".format(eBookFile))
            print("파일있음")
          except:
            print("파일없음")
        else:
          print("파일없음")

    print("revisionType:",revisionType)
    print("revisionDate:",revisionDate)
    print("codeVersion:",codeVersion)
    print("fileUrl:",fileUrl)
    print("revisionReasonFile:",revisionReasonFile)
    print("eBookFile:",eBookFile)
    print("===========================")
    revision_history.append({
      "revisionType":revisionType,
      "revisionDate":revisionDate,
      "codeVersion":codeVersion,
      "fileUrl":fileUrl,
      "revisionReasonFile":revisionReasonFile,
      "eBookFile":eBookFile
    })
  
  
  detailBox=soup.find('div',class_="detail_bx")
  introduction=detailBox.find_all('div',class_="ct_bx")[0].get_text().strip()
  tableOfContentsDiv=detailBox.find_all('div',class_="ct_bx")[2]
  tableOfContentsRows=tableOfContentsDiv.find_all('tr')
  tableOfContents=[]
  for tableOfContentsRow in tableOfContentsRows:
    tableOfContents.append(tableOfContentsRow.get_text().strip())
  checkList = detailBox.find_all('div',class_="ct_bx")[1].get_text().replace("\r","").replace("\t","").strip().split('\n')
  print("introduction:",introduction)
  print("tableOfContents:",tableOfContents)
  print("checkList:",checkList)
  infobase['KGS-CODE'][0]['metadata']['Type']=category_code
  infobase['KGS-CODE'][0]['metadata']['CreationDate']=CreationDate
  infobase['KGS-CODE'][0]['metadata']['ModDate']=ModDate
  infobase['KGS-CODE'][0]['metadata']['Category']=Category
  infobase['KGS-CODE'][0]['metadata']['FileName']=FileName
  
  infobase['KGS-CODE'][0]['data']['basic_info']['codeNumber']=codeNumber
  infobase['KGS-CODE'][0]['data']['basic_info']['category']=Category
  infobase['KGS-CODE'][0]['data']['basic_info']['koreanTitle']=koreanTitle
  infobase['KGS-CODE'][0]['data']['basic_info']['englishTitle']=englishTitle
  infobase['KGS-CODE'][0]['data']['basic_info']['lastRevisionDate']=ModDate
  infobase['KGS-CODE'][0]['data']['basic_info']['establishmentDate']=CreationDate
  infobase['KGS-CODE'][0]['data']['basic_info']['status']=status
  infobase['KGS-CODE'][0]['data']['basic_info']['comparisonFile']['fileName']=comparisonFile_fileName
  infobase['KGS-CODE'][0]['data']['basic_info']['comparisonFile']['fileUrl']=comparisonFile_fileUrl
  
  infobase['KGS-CODE'][0]['data']['revision_history']=revision_history
  infobase['KGS-CODE'][0]['data']['detail']['introduction']=introduction
  infobase['KGS-CODE'][0]['data']['detail']['tableOfContents']=tableOfContents
  infobase['KGS-CODE'][0]['data']['detail']['checkList']=checkList
  
  with open("result\\"+FileName, "w", encoding='utf-8') as file:
    json.dump(infobase, file, ensure_ascii=False, indent=2)
  return infobase


def MakeBucket():
    aws_access_key_id = os.getenv('aws_access_key_id')
    aws_secret_access_key = os.getenv('aws_secret_access_key')
    region_name = os.getenv('region_name')
    bucket_name = 'kgs-code'
    s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
    )
    try:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region_name}
        )
        print(f"버킷 {bucket_name} 생성 성공!")
    except Exception as e:
        print(f"버킷 생성 실패: {str(e)}")

    for year in range(2024, 2026):
        folder_name = f"{year}12"
        try:
            s3_client.put_object(Bucket=bucket_name, Key=(folder_name + '/'))
            s3_client.put_object(Bucket=bucket_name, Key=(f"kgs-code/attachments/{folder_name}/"))
            print(f"폴더 {folder_name} 및 kgs-code/attachments/{folder_name} 생성 성공!")
        except Exception as e:
            print(f"폴더 생성 실패: {str(e)}")

    for year in range(2025, 2026):
        for month in range(1, 13):
            folder_name = f"{year}{month:02d}"
            try:
                s3_client.put_object(Bucket=bucket_name, Key=(folder_name + '/'))
                s3_client.put_object(Bucket=bucket_name, Key=(f"kgs-code/attachments/{folder_name}/"))
                print(f"폴더 {folder_name} 및 kgs-code/attachments/{folder_name} 생성 성공!")
            except Exception as e:
                print(f"폴더 생성 실패: {str(e)}")

    for year in range(2026, 2027):
        folder_name = f"{year}12"
        try:
            s3_client.put_object(Bucket=bucket_name, Key=(folder_name + '/'))
            s3_client.put_object(Bucket=bucket_name, Key=(f"kgs-code/attachments/{folder_name}/"))
            print(f"폴더 {folder_name} 및 kgs-code/attachments/{folder_name} 생성 성공!")
        except Exception as e:
            print(f"폴더 생성 실패: {str(e)}")

    for year in range(2026, 2027):
        for month in range(1, 13):
            folder_name = f"{year}{month:02d}"
            try:
                s3_client.put_object(Bucket=bucket_name, Key=(folder_name + '/'))
                s3_client.put_object(Bucket=bucket_name, Key=(f"kgs-code/attachments/{folder_name}/"))
                print(f"폴더 {folder_name} 및 kgs-code/attachments/{folder_name} 생성 성공!")
            except Exception as e:
                print(f"폴더 생성 실패: {str(e)}")
def PrintS3FileNames():
    aws_access_key_id = os.getenv('aws_access_key_id')
    aws_secret_access_key = os.getenv('aws_secret_access_key')
    region_name = os.getenv('region_name')
    bucket_name = 'kgs-code'
    prefix=""
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )

    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        if 'Contents' in response:
            for obj in response['Contents']:
                print(obj['Key'])
        else:
            print("버킷에 파일이 없습니다.")
    except Exception as e:
        print("파일 목록을 가져오는 데 실패했습니다:", str(e))    
def DeleteS3FileNames():
    aws_access_key_id = os.getenv('aws_access_key_id')
    aws_secret_access_key = os.getenv('aws_secret_access_key')
    region_name = os.getenv('region_name')
    bucket_name = 'kgs-code'
    prefix = ""
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )

    try:
        # List all objects in the bucket
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        
        if 'Contents' in response:
            # Create a list of objects to delete
            objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
            
            # Delete all objects
            s3_client.delete_objects(
                Bucket=bucket_name,
                Delete={
                    'Objects': objects_to_delete,
                    'Quiet': False
                }
            )
            print(f"{len(objects_to_delete)}개의 파일이 삭제되었습니다.")
        else:
            print("버킷에 파일이 없습니다.")
    except Exception as e:
        print("작업 실패:", str(e))
def UploadImageToS3(inputData):
  # AWS 계정의 액세스 키와 시크릿 키를 설정합니다.
  timeNow=datetime.datetime.now().strftime("%Y%m")
  aws_access_key_id=os.getenv('aws_access_key_id')
  aws_secret_access_key=os.getenv('aws_secret_access_key')
  region_name=os.getenv('region_name')
  bucket_name='kgs-code'

  # S3 클라이언트를 생성합니다.
  s3_client = boto3.client(
      's3',
      aws_access_key_id=aws_access_key_id,
      aws_secret_access_key=aws_secret_access_key,
      region_name=region_name
  )
      
  try:
      response = s3_client.upload_file(
          Filename="result/{}".format(inputData['KGS-CODE'][0]['metadata']['FileName']),
          Bucket=bucket_name,
          Key=f"{timeNow}/{inputData['KGS-CODE'][0]['metadata']['FileName']}"  # timeNow(예: 202412) 폴더 안에 파일 저장
      )
      print("JSON파일 업로드 성공!")
  except Exception as e:
      print("파일 업로드 실패:", str(e))
      return None          
  
  comparison_file_name = inputData['KGS-CODE'][0]['data']['basic_info']['comparisonFile']['fileName']

  if comparison_file_name:
      try:
          response = s3_client.upload_file(
              Filename=f"result/{comparison_file_name}",
              Bucket=bucket_name,
              Key=f"attachments/{timeNow}/{comparison_file_name}"
          )
          print("비교 파일 업로드 성공!")
      except Exception as e:
          print("비교 파일 업로드 실패:", str(e))
  
  revision_history = inputData['KGS-CODE'][0]['data']['revision_history']
  if len(revision_history)>0:
    for index,revision in enumerate(revision_history):
      print("{}/{}번째 개정".format(index+1,len(revision_history)))
      if len(revision['revisionReasonFile'])>0:
        try:
          response = s3_client.upload_file(
              Filename=f"result/{revision['revisionReasonFile']}",
              Bucket=bucket_name,
              Key=f"attachments/{timeNow}/{revision['revisionReasonFile']}"
          )
          print("개정 파일 업로드 성공!")
        except Exception as e:
          print("개정 파일 업로드 실패:", str(e))
      if len(revision['eBookFile'])>0:
        try:
          response = s3_client.upload_file(
              Filename=f"result/{revision['eBookFile']}",
              Bucket=bucket_name,
              Key=f"attachments/{timeNow}/{revision['eBookFile']}"
          ) 
          print("전자책 파일 업로드 성공!")
        except Exception as e:
          print("전자책 파일 업로드 실패:", str(e))

def job():
  print("시작")
  load_dotenv()
  #===========폴더만들기
  # MakeBucket()
  #===========파일확인하기
  # DeleteS3FileNames()
  # PrintS3FileNames()

  #=============URL가져오기
  GetSearch()


  #=============상세정보 가져오기
  createFolder('result')
  infobase={
      "KGS-CODE": [
          {
              "metadata": {
                  "Type": "",
                  "Source": "https://cyber.kgs.or.kr/",
                  "Author": "가스기술기준정보시스템",
                  "CreationDate": "",
                  "ModDate": "",
                  "Category": "",
                  "FileName": ""
              },
              "data": {
                  "basic_info": {
                      "codeNumber": "",
                      "category": "",                    
                      "koreanTitle": "",
                      "englishTitle": "",
                      "lastRevisionDate": "",
                      "establishmentDate": "",
                      "status": "",
                      "comparisonFile": {
                          "fileName": "",
                          "fileUrl": ""
                      }
                  },
                  "revision_history": [],
                  "detail": {
                      "introduction": [],
                      "tableOfContents": [],
                      "checkList": []
                  }
              }
          }
      ]
  }
  with open("urlList.json", "r") as file:
    urlList = json.load(file)
  for index,item in enumerate(urlList):
    print("{}/{}번째 항목 작업중".format(index+1,len(urlList)))
    result=GetDetail(item,infobase)
    UploadImageToS3(result)
    print('===================================')
    break



  files = glob.glob('result/*')
  for f in files:
      os.remove(f)



# 매주 월요일 9시에 job 함수 실행
schedule.every().monday.at("09:00").do(job)
firstFlag=True
while True:
    if firstFlag:
        print("첫 실행")
        firstFlag=False
        job()
    print("현재시간은:",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    schedule.run_pending()
    time.sleep(10)  # 1분마다 체크
    

