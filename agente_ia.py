import os
import re
from typing import Any, Dict

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - fallback for environments without openai
    OpenAI = None


def analisar_produto(texto: str, contexto: str = "VOLUME_DESC") -> Dict[str, Any]:
    texto = texto or ""
    texto_lower = texto.lower()

    desconto_match = re.search(r"desconto[:\s]*(\d+)", texto_lower)
    desconto = int(desconto_match.group(1)) if desconto_match else 25

    palavras_chave = ["promo", "oferta", "desconto", "preço", "produto", "oferta"]
    tem_chave = any(palavra in texto_lower for palavra in palavras_chave)

    score = min(95, 60 + desconto // 2)
    if tem_chave:
        score = min(95, score + 5)

    aprovado = desconto >= 20 and score >= 60
    legenda = (
        "Oferta com bom potencial de conversão e desconto relevante."
        if aprovado
        else "Produto sem destaque suficiente para publicação neste momento."
    )

    # Verificar se OpenAI está habilitado
    enable_openai = os.getenv("ENABLE_OPENAI", "0").strip().lower() in ("1", "true", "yes")
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    
    if enable_openai and api_key and OpenAI is not None:
        try:
            client = OpenAI(api_key=api_key)
            system_msg = (
                "Você analisa produtos de oferta e responde em JSON com os campos aprovado, legenda e score."
            )

            # adaptar instrução ao contexto (vendas x popularidade)
            if contexto == "POPULARITY_DESC":
                user_hint = (
                    "Este produto foi identificado por alta popularidade/pesquisas. "
                    "Enfatize tendência, urgência e prova social na legenda quando relevante."
                )
            else:
                user_hint = (
                    "Este produto foi identificado por alto volume de vendas. "
                    "Enfatize confiança, provas sociais e urgência de compra na legenda."
                )

            response = client.responses.create(
                model="gpt-4.1-mini",
                input=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": f"{user_hint}\nAnalise este produto e responda em JSON: {texto}"},
                ],
            )
            content = getattr(response, "output_text", "") or ""
            if content:
                import json

                parsed = json.loads(content)
                if isinstance(parsed, dict):
                    return {
                        "aprovado": bool(parsed.get("aprovado", aprovado)),
                        "legenda": str(parsed.get("legenda", legenda)),
                        "score": int(parsed.get("score", score)),
                    }
        except Exception:
            pass

    # fallback local: adaptar legenda conforme contexto
    if contexto == "POPULARITY_DESC":
        legenda = (
            "Tendência: produto muito procurado — alta demanda. Ótimo para conversão rápida."
            if aprovado
            else "Produto com procura, mas sem destaque forte para publicação agora."
        )
    else:
        legenda = (
            "Top vendas: produto com histórico de vendas e boa conversão." 
            if aprovado
            else "Produto com vendas, mas sem destaque suficiente para publicar agora."
        )

    return {"aprovado": aprovado, "legenda": legenda, "score": score}
