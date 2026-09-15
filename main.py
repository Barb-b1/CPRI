import streamlit as st
import feedparser
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

st.set_page_config(page_title="PR Intel - Clipping", page_icon="❔", layout="wide")
st.title("❔ CPRI - Clipping Automático")
st.write("CPRI é uma plataforma que monitora notícias em tempo real e classifica como neutro, negativo ou positivo com IA.")

# AQUI VOCÊ MUDA O TEMA SEMPRE QUE QUISER
tema = st.text_input("Digite o tema que quer monitorar:", "Escreva aqui!")

def buscar_noticias(termo):
    import urllib.parse
    termo_codificado = urllib.parse.quote_plus(termo)
    url = f"https://news.google.com/rss/search?q={termo_codificado}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    feed = feedparser.parse(url)
    return [{"titulo": e.title, "link": e.link, "fonte": e.source.title if hasattr(e, 'source') else 'Google News'} for e in feed.entries[:5]]

def analisar(noticias, termo):
    texto = "\n".join([f"{i}. {n['titulo']}" for i, n in enumerate(noticias, 1)])
    prompt = f"""
    Você é um analista de PR. Analise 5 notícias sobre '{termo}':
    {texto}
    
    Para cada notícia, responda:
    - Sentimento: POSITIVO, NEGATIVO ou NEUTRO
    - Resumo: 1 frase
    - Risco: 0 a 10
    
    No final, dê um Resumo Geral da reputação.
    Formate bonito com emojis.
    """
    r = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
    return r.text

if st.button(f"⭕ Analisar {tema} agora"):
    with st.spinner(f"Buscando notícias sobre {tema}..."):
        noticias = buscar_noticias(tema)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader(f"📰 {len(noticias)} notícias")
        for n in noticias:
            st.write(f"**{n['titulo']}**")
            st.write(f"[{n['fonte']} - Ler matéria]({n['link']})")
            st.divider()

    with col2:
        with st.spinner("Analisando reputação com IA..."):
            analise = analisar(noticias, tema)
        st.subheader("🤖 Análise de Reputação")
        st.markdown(analise)
else:
    st.info("👆 Digite um tema acima e clique em Analisar. Ex: Louveira, Tecnologia, Política")