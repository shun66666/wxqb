import os

from minio import Minio
from minio.error import InvalidResponseError

from scrapy_sprider_project.settings import MINIO_HOST, MINIO_ACCESS_KEY, MINIO_SECRET_KEY

"""
minio版本
参考https://www.bookstack.cn/read/MinioCookbookZH/24.md
"""
from minio import Minio
from minio.error import MinioException


class MinioOperate():
    def __init__(self):
        self.minio_client = Minio(MINIO_HOST,
                                  access_key=MINIO_ACCESS_KEY,
                                  secret_key=MINIO_SECRET_KEY,
                                  region='cn-north-1',
                                  secure=False)

    def create_bucket(self, bucket):
        """
        1、先检查minio bucket是否存在，存在则返回True
        2、再通过client调用make_bucket
        3、创建成功则返回True，否则返回False
        :param bucket: String
        :return: bool
        """
        try:
            if self.minio_client.bucket_exists(bucket):
                return True
            self.minio_client.make_bucket("images")
        except MinioException as err:
            print(err)
            return False
        except ValueError as val_err:
            print(val_err)
            return False

    def bucket_exist(self, bucket):
        """
        判断bucket是否存在,存在返回True， 不存在返回False
        """
        return self.minio_client.bucket_exists(bucket)

    def delete_bucket(self, bucket):
        """
        删除minio中bucket
        :param bucket: bucket name
        :return: bool
        """
        try:
            if not self.minio_client.bucket_exists(bucket):
                print("桶子不存在")
                return False
            self.minio_client.remove_bucket(bucket)
            return True
        except ValueError:
            return False

    def fget_object(self, bucket, object_name, file_name):
        self.minio_client.fget_object(
            bucket, object_name, file_name)

    def fput_object(self, bucket, object_name, file_name):
        self.minio_client.fput_object(
            bucket, object_name, file_name)

    def exist_object(self, bucket, object_name):
        # Get a full object.
        try:
            data = self.minio_client.get_object(bucket, object_name)
            print(74, data)
            if data:
                print(f"图片{object_name}已下载")
                return 1
            else:
                print(f"图片{object_name}不存在")
                print(data)
                return 0
        except Exception as err:
            print(err)
            return 0


if __name__ == '__main__':
    bucket = "wxqb"
    print(1)
    minio_client = MinioOperate()
    print(2)
    flag = minio_client.bucket_exist(bucket)
    print(flag)
    # 获取上一层目录
    parPath = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    main_dir = os.path.join(parPath, "public_report")
    images_file_path = [os.path.join(main_dir, file_name) for file_name in os.listdir(main_dir)]
    for image_file_path in images_file_path:
        file_name = os.path.basename(image_file_path)
        file_name = "public_report/"+file_name
        print(file_name, image_file_path)
        # 判断文件是否存在，不存在则上传
        # flag = minio_client.exist_object(bucket, file_name)
        # print(flag)
        # if not flag:
        #     print(213123)
        #     minio_client.fput_object(bucket, file_name, image_file_path)
        #     # 上传成功后删除本地的文件
        #     os.remove(image_file_path)

