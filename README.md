# VK comic poster

Post comics to the wall of VK public page automatically!
 
## How to prepare:
1. Make sure Python installed on your PC - you can get it from [official website](https://www.python.org/).
   

2. Install libraries with pip:
    ```
    pip3 install -r requirements.txt
    ```
   
3. If you need to create a new VK group, this can be done at the [community creation page](https://vk.com/groups?tab=admin).
   Skip this step if the group has already been created.
   
4. Find out the group ID using a [special service](https://regvk.com/id/).
   Create .env file in directory with main.py file(use Notepad++) and add the string
    ```
    VK_GROUP_ID='your_group_id'
    ```
    to it instead of value in quotes. Here and further quotes must be removed.
   
5. Create an application on the [VK page for developers](https://vk.com/dev) using the "My Apps" button at the top of the page.
   Select the "standalone" application type.
   
6. On the [My Apps page](https://vk.com/apps?act=manage), click the "Manage" button and copy the application ID from the address bar.
   Save the ID in the .en file on a separate line.
   
7. Following the [instructions on Implict Flow](https://vk.com/dev/implicit_flow_user), get an access_token to access the VK API.
   Set the scope parameter as follows:
   ```scope = photos, groups, wall, offline```.
   The `redirect_uri` parameter should be removed from the request.
   As a result, you will get an `access_token` looks like `533bacf**********06a3` in the browser address bar.
   Add it to your .env file as a line:
   ```
   VK_ACCESS_TOKEN='your_access_token'
   ```

## How to use:
Run `main.py` with console. Use `cd` command if you need to change directory:
```
D:\>cd D:\learning\python\api_services\vk_comic_poster
D:\learning\python\api_services\vk_comic_poster>python main.py
```

## Available options
You can change the path for downloaded images using the console.
Get available options with `-h` argument:
```
D:\learning\python\api_services\vk_comic_poster>python main.py -h
usage: main.py [-h] [-c COUNT] [-dir DIRECTORY]

Загрузка комиксов xkcd на страницу Вконтакте

optional arguments:
  -h, --help            show this help message and exit
  -dir DIRECTORY, --directory DIRECTORY
                        Путь к папке для скачанных картинок
```
