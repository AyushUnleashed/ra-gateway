
import os
import pickle
from typing import List, Tuple
import whisper
from src.utils.logger import logger
import assemblyai as aai

def transcribe_video_whisper(video_path: str, model: whisper.Whisper) -> List[Tuple[List[str], float, float]]:
    """
    Transcribe the video using Whisper and return the sentences with their timings.
    """

    logger.info('Transcribing video')
    result = model.transcribe(video_path)

    sentences = []
    for segment in result["segments"]:
        words = segment["text"].strip().split()
        start_time = segment["start"]
        end_time = segment["end"]
        sentences.append((words, start_time, end_time))

    logger.info('Transcription complete')
    
    
    return sentences

def transcribe_video_assembly(video_path: str) -> List[Tuple[List[str], float, float]]:
    """
    Transcribe the video using Whisper and return the sentences with their timings.
    """
    logger.info('Transcribing video')

    transcriber = aai.Transcriber()

    transcript = transcriber.transcribe(video_path)
    sentences = transcript.get_sentences()

    setences_input = []
    for sentence in sentences:
        words = sentence.text.strip().split()
        start_time = sentence.start/1000.0
        end_time = sentence.end/1000.0
        setences_input.append((words, start_time, end_time))
    
    return setences_input

if __name__ == "__main__":
    video_path = "src/temp_storage/4c6c84ca-9a42-4618-b590-3cb866b7e4b2/assets/000_675f3f6f371f91c3d8aa055f_with_audio.mp4"
    
    # Transcribe using Whisper
    whisper_model = whisper.load_model("base")
    whisper_sentences = transcribe_video_whisper(video_path, whisper_model)
    print("Whisper Transcription:")
    print(whisper_sentences)
    
    # Transcribe using AssemblyAI
    assembly_sentences = transcribe_video_assembly(video_path)
    print("AssemblyAI Transcription:")
    print(assembly_sentences)
    
    # Compare the results
    if whisper_sentences == assembly_sentences:
        print("Both transcriptions are identical.")
    else:
        print("The transcriptions differ.")