
from src.config.module import enviroiments


#chama a função que retorna a instancia do redis e junta com as variaveis de ambiente
from src.cache.manage import cache_control
client = cache_control(host=enviroiments["redis_host"], port=enviroiments["redis_port"], 
                       password=enviroiments["redis_password"])





