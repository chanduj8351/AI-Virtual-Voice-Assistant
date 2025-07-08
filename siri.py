import asyncio
#from brain.main import Brain
from fn_exec import functioncall
from core.tts import SpeechSynthesizer
from core.stt import telugu_speech_recognition as stt

async def handle_speech(results):
    """Run TTS for all results concurrently using async wrapper."""
    synthesizer = SpeechSynthesizer()
    tasks = []
    for result in results:
        if 'response' in result:
            tasks.append(synthesizer.speak_async(result['response']))
    await asyncio.gather(*tasks)

async def main():
    from rich import print
    from rich.columns import Columns
    from rich.panel import Panel

    print(Panel.fit("🤖 [bold green]Parallel Command Executor v2.0[/]"))

    while True:
        try:
            user_input = input("\n ➤  ")
            #user_input = stt()
            if user_input.lower() in ('exit', 'quit'):
                break

            results = functioncall(user_input)

            print("\n🔍 Results:")
            panels = []

            for result in results:
                if 'function' in result and result['function'] in ['assistant_response', 'assistant_message']:
                    content = [
                        f"🤖  {result['response']}",
                        f"⏱️  Total Processing Time: {result['execution_time']}s"
                    ]
                    panels.append(Panel("\n".join(content), border_style="blue", title="Assistant Response"))
                else:
                    content = [
                        f"⚡ [bold]{result.get('function', 'unknown')}[/]",
                        f"⌚ Time: {result.get('execution_time', 0)}s",
                        f"✅ Success: {result.get('result', False)}"
                    ]
                    if result.get('error'):
                        content.append(f"❌ [red]Error: {result['error']}[/]")
                    else:
                        content.append(f"📤 Response: {result.get('response', '')}")
                    panels.append(Panel("\n".join(content),
                                        border_style="green" if result.get('result', False) else "red"))

            print(Columns(panels))

            await handle_speech(results)

        except KeyboardInterrupt:
            print("\n🚫 Operation cancelled by user")
            break
        except Exception as e:
            print(f"💥 Critical error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
    #Brain().scheduled_self_training()
















































import asyncio
#from brain.main import Brain
from fn_exec import functioncall
from core.tts import SpeechSynthesizer
from core.stt import run
import sys
#from core.stt import telugu_speech_recognition as stt

async def handle_speech(results):
    """Run TTS for all results concurrently using async wrapper."""
    synthesizer = SpeechSynthesizer()
    tasks = []
    for result in results:
        if 'response' in result:
            tasks.append(synthesizer.speak_async(result['response']))
    await asyncio.gather(*tasks)

async def main():
    from rich import print
    from rich.columns import Columns
    from rich.panel import Panel

    print(Panel.fit("🤖 [bold green]Parallel Command Executor v2.0[/]"))

    while True:
        try:
            user_input = input("\n ➤  ")
            #user_input = run()
            with open("transcript.txt", "w", encoding='utf-8') as f: f.write(user_input)

            with open("transcript.txt", "r", encoding='utf-8') as f:
                query = f.read()


            try:
                if query:    
                    results = functioncall(query)

                    print("\n🔍 Results:")
                    panels = []

                    for result in results:
                        if 'function' in result and result['function'] in ['assistant_response', 'assistant_message']:
                            content = [
                                f"🤖  {result['response']}",
                                f"⏱️  Total Processing Time: {result['execution_time']}s"
                            ]
                            panels.append(Panel("\n".join(content), border_style="blue", title="Assistant Response"))
                        else:
                            content = [
                                f"⚡ [bold]{result.get('function', 'unknown')}[/]",
                                f"⌚ Time: {result.get('execution_time', 0)}s",
                                f"✅ Success: {result.get('result', False)}"
                            ]
                            if result.get('error'):
                                content.append(f"❌ [red]Error: {result['error']}[/]")
                            else:
                                content.append(f"📤 Response: {result.get('response', '')}")
                            panels.append(Panel("\n".join(content),
                                                border_style="green" if result.get('result', False) else "red"))

                    print(Columns(panels))

                    await handle_speech(results)
        
            except:
                print("Error: ", sys.exc_info()[0])

        except KeyboardInterrupt:
            print("\n🚫 Operation cancelled by user")
            break
        except Exception as e:
            print(f"💥 Critical error: {str(e)}")

# if __name__ == "__main__":
#     asyncio.run(main())
   


   
















# from fn_exec import functioncall
# from core.tts import SpeechSynthesizer
# from core.stt import telugu_speech_recognition  # Ensure correct import path

# def main():
#     from rich import print
#     from rich.columns import Columns
#     from rich.panel import Panel

#     print(Panel.fit("🤖 [bold green]Parallel Command Executor v2.0[/]"))

#     while True:
#         try:
#             user_input = telugu_speech_recognition()
#             if not user_input:
#                 continue
#             if user_input.lower() in ('exit', 'quit'):
#                 break

#             results = functioncall(user_input)
#             panels = []

#             for result in results:
#                 stt.mute_mic()  # 🔇 Mute mic before speaking
#                 SpeechSynthesizer().speak(result['response'])
#                 stt.unmute_mic()  # 🔊 Unmute mic after speaking

#                 if 'function' in result and result['function'] in ['assistant_response', 'assistant_message']:
#                     content = [
#                         f"💬 {result['response']}",
#                         f"⏱️  Total Processing Time: {result['execution_time']}s"
#                     ]
#                     panels.append(Panel("\n".join(content), border_style="blue", title="Assistant Response"))
#                 else:
#                     content = [
#                         f"⚡ [bold]{result.get('function', 'unknown')}[/]",
#                         f"⌚ Time: {result.get('execution_time', 0)}s",
#                         f"✅ Success: {result.get('result', False)}"
#                     ]
#                     if result.get('error'):
#                         content.append(f"❌ [red]Error: {result['error']}[/]")
#                     else:
#                         content.append(f"📤 Response: {result.get('response', '')}")
#                     panels.append(Panel("\n".join(content), border_style="green" if result.get('result', False) else "red"))

#             print(Columns(panels))

#         except KeyboardInterrupt:
#             print("\n🚫 Operation cancelled by user")
#             break
#         except Exception as e:
#             print(f"💥 Critical error: {str(e)}")

# # if __name__ == "__main__":
# #     main()
