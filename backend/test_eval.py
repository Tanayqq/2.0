import sys, os
sys.path.insert(0, os.path.abspath('backend'))
from eval.eval_harness import calculate_metrics
from app.domain.models import MedicalQuery
from app.api.dependencies import get_llm_provider, get_embedding_model, get_vector_db, get_cross_encoder
from app.usecases.rag_usecase import ProcessClinicalQueryUseCase

print("Initializing RAG dependencies...")
llm_provider = get_llm_provider()
embedding_model = get_embedding_model()
vector_db = get_vector_db()
cross_encoder = get_cross_encoder()

usecase = ProcessClinicalQueryUseCase(
    llm_provider=llm_provider,
    embedding_model=embedding_model,
    vector_db=vector_db,
    cross_encoder=cross_encoder
)

item = {
    'question': 'What are the contraindications of Metformin?',
}
query = MedicalQuery(question=item['question'])
try:
    response = usecase.execute(query)
    print(response.model_dump_json(indent=2))
except Exception as e:
    import traceback
    traceback.print_exc()
