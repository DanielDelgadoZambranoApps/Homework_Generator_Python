import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import initialize_app, storage

import json
from llama_cpp import Llama

#llama_cpp(model_path=model, verbose=True, n_ctx=2048) ????

def main():
    cred = credentials.Certificate("ServiceAccountKey.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    results = db.collection('Homework Solicitudes').get()

    print("Running Model ---------> ")
    llm = Llama(model_path="./models/gpt4all-lora-quantized-ggml.bin", verbose=True, n_ctx=4096)
 #  llm = Llama(model_path="./models/gpt4all-lora-quantized-ggml.bin", verbose=True)

    if (results):
        Total_Answers = []
        for homeworkData in results :
            
            db_local = firestore.client()
            db_local.collection('Homework Solicitudes').document(homeworkData.to_dict()['mail']).update({"inProgress":True})   
            
            if(homeworkData):
                if(homeworkData.to_dict()['not_generated_Homework']):

                    current_homework_ref = db.collection('Homework Solicitudes').document(homeworkData.to_dict()['mail']).collection('All_Homeworks').document(homeworkData.to_dict()['not_generated_Homework']).get()
                    print("Generando textos para la siguiente tarea --->  " + homeworkData.to_dict()['not_generated_Homework'])
                    print("Main Content (Texto Principal) ------------> "+ current_homework_ref.to_dict()['Main_content'])

                    output = llm(
                    "Write a 2 pages essay on "+ current_homework_ref.to_dict()['Main_content'] + " Answer:",
                    #   homeworkSubData.to_dict()['content'] + " Answer:",
                        max_tokens=2048,
                    #    top_p=1.0,
                    #   temperature=0.8,
                    #   stop=["\n", "Question:", "Q:"],
                        echo=True
                    )
                    Total_Answers.append(output['choices'][0]['text'])
                    print(output['choices'][0]['text'])

                    for current_sub_topic in range(len(current_homework_ref.to_dict()['subTopicsArray'])) :
                        print("Generando texto para sub-topic ------------> "   +  current_homework_ref.to_dict()['subTopicsArray'][current_sub_topic]['contenido'])

                        sub_output = llm(
                        "Write a 2 pages essay on "+  current_homework_ref.to_dict()['subTopicsArray'][current_sub_topic]['contenido'] + " Answer:",
                        #   homeworkSubData.to_dict()['content'] + " Answer:",
                            max_tokens=2048,
                        #    top_p=1.0,
                        #   temperature=0.8,
                        #   stop=["\n", "Question:", "Q:"],
                            echo=True
                        )
                        Total_Answers.append(sub_output['choices'][0]['text'])
                        print(sub_output['choices'][0]['text'])

                current_homework_ref = db.collection('Homework Solicitudes').document(homeworkData.to_dict()['mail']).collection('All_Homeworks').document(homeworkData.to_dict()['not_generated_Homework']).update({'All_Generated_Texts':Total_Answers})
                current_homework_ref = db.collection('Homework Solicitudes').document(homeworkData.to_dict()['mail']).collection('All_Homeworks').document(homeworkData.to_dict()['not_generated_Homework']).update({'isGenerated':True})

                db_local.collection('Homework Solicitudes').document(homeworkData.to_dict()['mail']).update({"not_generated_Homework":None})  
                db_local.collection('Homework Solicitudes').document(homeworkData.to_dict()['mail']).update({"done":True})   
                
if __name__ == "__main__":
    main()