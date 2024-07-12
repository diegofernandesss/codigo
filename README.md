## Sobre o Projeto

``` O Projeto é da disciplina de Engenharia de Software do PPGTI do IFPB. Em breve mais informações!```

## Instalando virtual enviroment
  ```
  $ sudo pip3 install virtualenv
  ```
  ```
  $ virtualenv venv
  ```


## Ativação e desativação
  ```
  $ source venv/bin/activate
	$ deactivate
  ```

- Instalando as dependências

  ```
  $ pip install -r requirements.txt
  ```

## Controle de versões de banco de dados
```
$ flask db init
```

```
$ flask db migrate -m "Initial migration."
```

```
$ flask db upgrade
```
