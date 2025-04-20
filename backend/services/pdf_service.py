from core.config import settings
# from core.logging import logger
# from models import Hashtag, HashtagCreate, HashtagUpdate, HashtagListItem
# from utils.hashtag_normalization import normalize_hashtag
# from utils.hashatag_description import placeholder_hashtag_description
# from utils.embeddings import mock_embedding, average_embeddings

from utils.hashtag_normalization import normalize_hashtag
from elasticsearch import AsyncElasticsearch, NotFoundError
from typing import List, Dict
import fitz
import io
import openai
import re


class PdfService:
    def __init__(self, es: AsyncElasticsearch):
        self.es = es
        self.index = settings.es_hashtag_index

    async def extract_title(self, doc) -> str:
        meta_title = doc.metadata.get("title", "").strip()
        # print(doc.metadata)
        if meta_title:
            return meta_title

        # if metadata does not have title, try to extract from the first page
        if len(doc) == 0:
            return ""

        first_page = doc.load_page(0)
        blocks = first_page.get_text("dict")["blocks"]

        # find the biggest font size in the first page
        text_candidates = []
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span["bbox"][0] > 100 and span["bbox"][2] < 500:  # x coordinates
                            text_candidates.append((span["size"], span["text"]))

        if not text_candidates:
            return ""
        # print(text_candidates)
        max_size = max(text_candidates, key=lambda x: x[0])[0]
        # print("max_size", max_size)
        # get all text with the same size as max_size
        title_candidates = [text for size, text in text_candidates if size > max_size - 0.2]
        return " ".join(title_candidates)


    async def extract_abstract(self, doc) -> str:
        first_page = doc.load_page(0)
        text = first_page.get_text()
        lowered = text.lower()
        result = None
        if "abstract" in lowered:
            idx = lowered.find("abstract") + len("abstract") + 1
            after_abstract = text[idx:].strip()
            # print(after_abstract)
            match = re.search(r'^(.*?)(?:\nINTRODUCTION\b)', after_abstract, re.DOTALL | re.MULTILINE)
            if match is None:
                match = re.search(r'^(.*?)(?:I\.\sINTRODUCTION\b)', after_abstract, re.DOTALL | re.MULTILINE)
            if match is None:
                match = re.search(r'^(.*?)(?:1\sINTRODUCTION\b)', after_abstract, re.DOTALL | re.MULTILINE)
            if match is None:
                match = re.search(r'^(.*?)(?:\nIntroduction\b)', after_abstract, re.DOTALL | re.MULTILINE)
            if match is None:
                match = re.search(r'^(.*?)(?:I\.\sIntroduction\b)', after_abstract, re.DOTALL | re.MULTILINE)
            if match is None:
                match = re.search(r'^(.*?)(?:1\sIntroduction\b)', after_abstract, re.DOTALL | re.MULTILINE)
            if match is not None:
                result = match.group(1).strip()[:7000]

        if not result:
            result = text[:7000]
        return result

    async def generate_hashtags(self, abstract):

        openai.api_key = "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"
        prompt = '''
        Given the following abstract, give me 10 terms of topics or classification or keywords.
        7 of terms should be common, broad, general in papers and 3 are more specific to abstract,
        please output only one line.
        term should be no more than three words, 
        start with uppercase letters,
        be separated by commas, and contain no other text, and no any symbol characters.
        No need to exist in abstract
        '''
        prompt += abstract
        response = openai.responses.create(
            model="gpt-4o-mini",
            input = prompt
        )
        return response.output_text
    
    async def extract_pdf_info(self, contents: bytes) -> Dict:
        try:
            doc = fitz.open(stream=io.BytesIO(contents), filetype="pdf")

            title = await self.extract_title(doc)
            # print("Title:", title)
            # print()
            abstract = await self.extract_abstract(doc)
            # print("Abstract:", abstract)
            # print()
            hashtags = await self.generate_hashtags(abstract)
            hashtags = [hashtag.strip() for hashtag in hashtags.split(",")]
            print("Hashtags:", hashtags)
            exist_hashtags = []
            for hashtag in hashtags:
                try:
                    hashtag = normalize_hashtag(hashtag)
                    await self.es.get(index=settings.es_hashtag_index, id=hashtag)
                    # print("Hashtag:", hashtag)
                    exist_hashtags.append(hashtag)
                except NotFoundError:
                    continue

            return {
                "title": title,
                "hashtags": exist_hashtags,
            }
        except Exception as e:
            return {"error": f"Failed to parse PDF: {str(e)} extract_pdf_info"}, 500