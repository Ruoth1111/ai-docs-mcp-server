#create AI webscrapping tool and will do it by following the 3 steps
#step 1: search the web for the information you need
import http.client
import json
import os
from dotenv import load_dotenv
import httpx
import asyncio
from fastmcp import FastMCP
from utils import clean_html_to_txt,get_response_from_llm
load_dotenv()

mcp= FastMCP("docs")

SERPER_URL="https://google.serper.dev/search"


async def search_web(query: str) -> dict| None:
    payload = json.dumps({
    "q": query,"num": 2
    })
    headers = {
    'X-API-KEY': os.getenv("SERPER_API_KEY"),
    'Content-Type': 'application/json'
    }

    
    #conn = http.client.HTTPSConnection("google.serper.dev")
    async with httpx.AsyncClient() as client:
        #now will remove this oldof post reqesut as with async await is used
        #conn.request("POST", "/search", payload, headers)
        response= await client.post(
            SERPER_URL,headers=headers,data=payload,timeout=30.0
        )
        #it works when response is not succesfull any error occurs,then it thorws errors anf gives info about it
        response.raise_for_status()
        return response.json()
        #and will remove this lower lines of code
        # res = conn.getresponse()
        # data = res.read()
        # return (data.decode("utf-8"))



#step 2: open official documentation for the tool you are using

async def fetch_url(url :str):
    #client 
    async with httpx.AsyncClient() as client:
        #hit req to url
        response= await client.get(
            #serper_url ni ab main url jo user dega vo use krenge
                url,timeout=30.0
            )
        #parse and clean data
        #cleaned_data=clean_html_to_txt(response.txt)
        system_prompt = "You are an AI Web scraper. Only return valid text, remove and clean every other HTML component that is not required."
               
        # Split response into chunks of 4000 characters
        chunk_size = 4000
        text_chunks = [response.text[i:i+chunk_size] for i in range(0, len(response.text), chunk_size)]
        
        cleaned_parts = []
        for chunk in text_chunks:
            cleaned_chunk = get_response_from_llm(
            user_prompt=chunk, 
            system_prompt=system_prompt, 
            model="openai/gpt-oss-20b"
            )
            cleaned_parts.append(cleaned_chunk)
        
        cleaned_response = "".join(cleaned_parts)

        #return cleaned data
        return cleaned_response



#step 3: Read the documentation and understand the tool and write code accordingly
#hm yha limit krenge tool ko ki saare link pr na jaakr bs particular official link pr jaaye
docs_urls= {
    "langchain":"python.langchain.com/docs",
    "lama-index":"docs.llamaindex.ai/en/stable",
    "openai":"platform.openai.com/docs",
    "uv":"docs.astral.sh/uv",
}
@mcp.tool()
async def get_docs(query: str, library: str):
    """
    Search the latest docs for a given query and library.
    Supports langchain, openai, llama-index and uv.

    Args:
        query: The query to search for (e.g. "Publish a package with UV")
        library: The library to search in (e.g. "uv")

    Returns:
        Summarized text from the docs with source links.
    """
    print("GET_DOCS CALLED")
    if library not in docs_urls:
        raise ValueError(f"Library {library} not supported by this tool")
    
    print("LIBRARY OK")
    query = f"site:{docs_urls[library]} {query}"

    print("SEARCHING...")
    results = await search_web(query)

    print("SEARCH COMPLETE")
    print(results)

    if len(results["organic"]) == 0:
        return "No results found"
    
    text_parts = []
    for result in results["organic"]:
        link = result.get("link", "")
        raw = await fetch_url(link)
        if raw:
            labeled = f"SOURCE: {link}\n{raw}"
            text_parts.append(labeled)
    return "\n\n".join(text_parts)
        

def main():
    mcp.run(transport="stdio")
    

if __name__ == "__main__":
    main()