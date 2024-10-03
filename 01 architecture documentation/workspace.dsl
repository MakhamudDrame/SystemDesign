workspace {
    name "profi.ru"
    description "Архитектура приложения profi.ru для управления пользователями, услугами и заказами"

    !identifiers hierarchical

    model {
       u1 = person "Клиент"
       u2 = person "Исполнитель заказа"
       u3 = person "Администратор"
    
       
       s1 = softwareSystem "Авторизация" 
       s2 = softwareSystem "Приложение"{

        -> s1 "Создание аккаунта, авторизация"

        data = container "База данных" {
            technology "PostgreSQL"
            description "База данных для хранения пользователей"
        }
 
        
        deals = container "Заказы" {
            technology "Django 4.2"
            description "Шаблоны для работы с заказами"
            -> s2.data "Создание заказа и отправка заказа в БД" 
        }

        servises = container "Услуги"{
            technology "Django 4.2"
            description "Шаблоны для работы с услугами"
            -> s2.data "Создание новой услуги и отправка услуги в БД"
            -> s2.deals "Добавляет заказ" {
                tags ex
            }
        }

        API = container "API Gateway" {
            technology "Django 4.2"
            description "Шаблоны для работы с услугами и заказами"
            -> servises "Создание и поиск услуг"
            -> deals "Содание и поиск заказов"
            
            
        }
        app = container "Приложение" {
            technology "React, JavaScript"
            description "Веб-приложение для взаимодействия с пользователями"
            -> API "Связь с сервером"
            
        }
       
       u3 -> s2.data "Получение данныйхх об услугах, заказах и пользователях"
      
       }
       
      
       
       u1 -> s2.app "Открывает приложение" 
       u2 -> s2.app "Открывает приложение" 
       s2.app -> s1 "Авторизация"
        

       u1 -> s1 "Регистрация, авторизация"  {
               tags "ex1"
       }
       
       u2 -> s1 "Регистрация, авторизация"   {
               tags "ex1"
       }
       
       

       s2.data -> s2.deals "Заказ попадает в список заказов исполнителя" {
                tags "ex"
            }
       
       s2.deals -> s2.app "Исполнитель получает информацию о заказе" {
                tags "ex"
            }

       s2.app -> u2 "Исполнитель берет заказ в работу " {
                tags "ex"
            }
    
       
       s1 -> s2.API "Соединение с сервером" {
                tags "ex"
            }
       u2 -> u1 "Пользователь получает заказ" {
                tags "ex"
            }



       
       
    deploymentEnvironment "Production" {

        deploymentNode "DMZ"{
            containerInstance s2.servises
            containerInstance s2.deals
            containerInstance s2.app
        }

        deploymentNode "Inside" {
            containerInstance s2.data
            
        }
    }
       

    }

    views {
        themes default

        systemContext s1 {
            include *
            exclude relationship.tag==ex
            autoLayout
        }

        container s2 {
            include *
            autoLayout lr
            exclude relationship.tag==ex
            exclude relationship.tag==ex1
        }

        deployment * "Production"   {
            include *
            autoLayout lr

        }
        dynamic s2 "001c" "Работа приложения" {
            autoLayout lr
            u1 -> s2.app "Открывает приложение"
            s2.app -> s1 "Авторизация"
            s1 -> s2.API "Соединение с сервером"
            s2.API -> s2.servises "Выбирает услугу"
            s2.servises -> s2.deals "Добавляет заказ"
            s2.deals -> s2.data "Заказ создается и фиксируется в БД" 
            s2.data -> s2.deals "Заказ попадает в список заказов исполнителя"
            s2.deals -> s2.app "Исполнитель получает информацию о заказе"
            s2.app -> u2 "Исполнитель берет заказ в работу "
            u2 -> u1 "Исполнитель оказывает улугу"


             
        }
        
    }
}


