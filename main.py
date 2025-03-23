import os

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
  """Example Hello World route."""
  name = os.environ.get("NAME", "World")
  return f"Hello {name}!"


from gemini import genai_blueprint
app.register_blueprint(genai_blueprint, url_prefix='/genai')

from checking import checking_blueprint
app.register_blueprint(checking_blueprint, url_prefix='/checking')


if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))