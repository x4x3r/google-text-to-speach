import os
import math
import google.cloud.texttospeech as tts
import io
import wave

def read_input(input_files: list) -> str:
    """read each input text file"""
    for input_file in input_files:
        with open(input_file, 'r') as f:
            input_text = f.read()
    return input_text

def split_input(input_text, chunk_size=40) -> str:
    """Split the input file into chunks"""
    num_chunks = math.ceil(len(input_text)/chunk_size)
    text_chunks = [input_text[i:i+chunk_size] for i in range(0, len(input_text), chunk_size)]
    return text_chunks

def text_to_speech(text_chunks, voice_name='en-US-Wavenet-D', audio_encoding='LINEAR16', sample_rate_hertz=24000):
    """convert text to speech"""
    
    # Set up Google Cloud credentials
    os.environ["GOOGLE_APPLICAION_CREDENTIALS"] = "key.json"

    # Create Text-to-Speech client
    client = tts.TextToSpeechClient()

    # Set the text input voice paramters
    voice_params = tts.VoiceSelectionParams(
        language_code='en-US',
        name=voice_name
    )

    # Set the audio output parameters
    audio_config = tts.AudioConfig(
        audio_encoding=audio_encoding,
        sample_rate_hertz=sample_rate_hertz
    )

    # Create a list to hold the audio content of each chunk
    audio_chunks = []

    # Perform the text-to-speech conversion for each chunk
    for i, text_chunk in enumerate(text_chunks):
        synthesis_input = tts.SynthesisInput(text=text_chunk)
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice_params,
            audio_config=audio_config
        )
    
        # Save the output audio content to a buffer
        audio_chunks.append(response.audio_content)

    return audio_chunks

def merge_chunks(audio_chunks, sample_rate_hertz):
    """Merge the audio chunks into a single WAV file"""
    output_buffer = io.BytesIO()
    with wave.open(output_buffer, 'wb') as output_wav:
        output_wav.setchannels(1)
        output_wav.setsampwidth(2)
        output_wav.setframerate(sample_rate_hertz)
        for chunk in audio_chunks:
            output_wav.writeframes(chunk)


def write_output(output_file, output_buffer):
    """Write the output file to disk"""
    with open(output_file, 'wb') as out:
        out.write(output_buffer.getvalue())
        print(f'Audio content written to file "{output_file}"')

if __name__ == "__main__":
    # Define input and output files
    input_files = ['test_input.txt']
    output_file = 'test_output.wav'

    # Read input file
    input_text = read_input(input_files)

    # Split input file into chunks
    text_chunks = split_input(input_text)
    print(text_chunks)

    # Convert text to speech
    audio_chunks = text_to_speech(text_chunks)

    # Merge audio chunks into single WAV file
    merged_audio = merge_chunks(audio_chunks, sample_rate_hertz=24000)

    # Write output file to disk
    write_output(output_file, merged_audio)