from crewai.tools import BaseTool
from typing import Type, List
from pydantic import BaseModel, Field
from docling.document_converter import DocumentConverter, PdfFormatOption, ImageFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, AcceleratorOptions, AcceleratorDevice
from qdrant_client import QdrantClient
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
import os
import uuid


qdrant_path = os.getenv('QDRANT_PATH')
collection_name = os.getenv('COLLECTION_NAME')

class UniversalParserInput(BaseModel):
    filenames: List[str] = Field(...,description="A list of names of the files to be parsed")


class UniversalParserTool(BaseTool):
    name: str = "Universal Parser Tool"
    description: str = "Used to parse all the defined types of files and Extracts inforamtion from the file"

    args_schema: Type[BaseModel] = UniversalParserInput

    def _run(self, filenames: List[str]) -> str:
        final_report = []
        
        # file checking
        file_dir = os.getenv('LOCAL_FILES_DIR')
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        # creating connection to qdrant
        client = QdrantClient(path=qdrant_path)

        # Parser config to run on CPU 
        cpu_options = AcceleratorOptions(
                num_threads=12,
                device=AcceleratorDevice.CPU
        )

        pdf_options = PdfPipelineOptions()
        pdf_options.do_ocr = True
        pdf_options.do_table_structure = True
        pdf_options.accelerator_options = cpu_options

        document_conv = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_options),
                InputFormat.IMAGE: ImageFormatOption(pipeline_options=pdf_options) 
              }
           )
        
        for filename in filenames:
            try:
                
                
                file_path = os.path.join(file_dir, filename)
                if not os.path.exists(file_path):
                    final_report.append(f"File dosen't exists: {filename}")
                    continue


                # Parsing of document
                res = document_conv.convert(file_path)

                file_md = os.path.splitext(filename)[0] + '.md'
                file_md_path = os.path.join(file_dir, file_md)


                # writing parsed document to file
                content = res.document.export_to_markdown()
                with open(file_md_path, "w", encoding="utf-8") as f:
                    f.write(content)


                # chunking markdown to store in qdrant
                chunks = self.make_chunks(markdowntext=content)
                text = [c.page_content for c in chunks]
                clean_filename = os.path.basename(filename)
                print(f"{filename}\n{clean_filename}")
                metadata = [{"source" :clean_filename, "chunk_id": i} for i in range(len(text))]

                if not client.collection_exists(collection_name):
                    client.create_collection(
                        collection_name=collection_name,
                        vectors_config=client.get_fastembed_vector_params()
                    )


                # saving to DB
                client.add(
                    collection_name=collection_name,
                    documents=text,
                    metadata=metadata,
                    ids=[str(uuid.uuid4()) for _ in text]
                )


                final_report.append(f"Successfully stored {len(text)} chunks from {filename} document.")


            except Exception as e:
                final_report.append(f"Error occured: {e}")
        
        
        return "\n".join(final_report)



    def make_chunks(self,markdowntext: str):
        headers_to_spliton = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3")
        ]

        markdownsplitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_spliton)
        md_header_split = markdownsplitter.split_text(markdowntext)

        text_split = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        return text_split.split_documents(md_header_split)