1.	Abrir Ambiente Vitual: "python -m venv .venv"
2.	Adicione Python as Variáveis de Ambiente (Troque {User} pelo nome da sua máquina): $env:Path += ";C:\Users\{User}\AppData\Local\Programs\Python\Python313\Scripts"		
3.	Instale as dependências: pip install -r requirements.txt
4. Rodar Aplicação: py main.py
5. Gerar Executável: PyInstaller main.spec