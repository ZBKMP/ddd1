class Dog:
    def speak(self):
        return "Woof!"

class Cat:
    def speak(self):
        return "Meow!"

# 工厂函数 用于生成特定对象的函数
def animal_factory(animal:str):
    if animal == 'dog':
        return Dog()
    elif animal == 'cat':
        return Cat()
    else:
        raise ValueError("no such animal")

animal= animal_factory('dog')
print(animal.speak())


#面相对象设计模式 : 工厂模式