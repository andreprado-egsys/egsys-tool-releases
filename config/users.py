"""Gerenciamento de usuários e autenticação."""
import hashlib

USUARIOS_AUTORIZADOS = {
    'andre.prado': ('257cff47721be2737b0e790813950f87', '8629afcfab6328f79cdc1610e929db4c07d35d360450d35ebb921153638889d2'),
    'lucas.serafim': ('e0d534a464369a1186f95de076a52be4', '8b08b1afa191d4ae747362cb158ae496a61f00c16dc29876b432fa6cbc38e784'),
    'joao.sopran': ('5a0473f88da2879f969ec49460024df7', '1a1002b156d4c96bb512854c3d1f4643332cea451bbfb71dfbb24901ab039c14'),
    'cassia.domingos': ('1bfc6ca0628b1b785a6470a700a385d0', 'ebf8a11aa17b72bda99a9ce9e6c88edf11f83ceeace8df14110f92a1d83d22b4'),
    'adenir.felipe': ('8fa9f19e50569903e5bd8b0167af9e9d', '3e7a8f2a18d0527d993584f60414d2b7b9cf7d9e328e0d897af65ba9aa1a9e12'),
    'camilo.egsys': ('ac2cd8c2c0bd6dba3041189031bfe84a', '2e835d6091c824f4c0fe881688c9f204165b4d4aca368ceea26c5f47744019b0'),
    'murilo.egsys': ('3cfc7ed611da32e9e59c968aeee52a02', '9f4471058b9170f443a244979dfc9a142e3c9f10185e63f66d7ba2f98e468ddb'),
}

def validar_credenciais(username, password):
    """Valida credenciais do usuário."""
    if username not in USUARIOS_AUTORIZADOS:
        return False
    
    sal_armazenado, hash_armazenado = USUARIOS_AUTORIZADOS[username]
    senha_com_sal = sal_armazenado + password
    hash_digitado = hashlib.sha256(senha_com_sal.encode()).hexdigest()
    
    return hash_digitado == hash_armazenado
