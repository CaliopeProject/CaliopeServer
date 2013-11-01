import json

class AccessControl:

  def __init__(self, configuration):
    self.config = json.loads(configuration)

def main():
          ac = AccessControl(open('permissions.json').read())

if __name__ == "__main__":
    main()
