prompt_template = {
   "temperature": 0.7,
   "max_tokens": 1000,
   "top_p": 0.9,
   "model": "gpt-4o",
   "stream": True,
   "messages": [
       {
           "role": "system",
           "content": [
               {
                   "type": "text",
                   "text": "You are a helpful assistant."
               }
           ]
       },
       {
           "role": "user",
           "content": [
               {
                   "type": "text",
                   "text": "Hello! tell me about this image",
                   "cache": True
               }
           ]
       }
   ],
}
