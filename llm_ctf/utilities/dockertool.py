import docker

class DockerClient:
    def __init__(self) -> None:
        self.client = docker.from_env()
        
    def get_images(self):
        images = self.client.images.list()
        image_names = [image.tags[0] if image.tags else "<none>:<none>" for image in images]
        return image_names
    

if __name__ == "__main__":
    d = DockerClient()
    print(d.get_images())