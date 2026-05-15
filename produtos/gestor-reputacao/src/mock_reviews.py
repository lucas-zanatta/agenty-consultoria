"""
Avaliações fictícias para testar o fluxo completo sem a API do Google.
Ativado quando MOCK_MODE=true no .env
"""

MOCK_REVIEWS = [
    {
        "reviewId": "mock-001",
        "name": "accounts/000/locations/000/reviews/mock-001",
        "starRating": "FIVE",
        "reviewer": {"displayName": "Ana Paula Souza"},
        "comment": "Serviço incrível! A equipe foi super atenciosa e o resultado ficou muito acima do esperado. Com certeza voltarei!",
        "createTime": "2026-05-14T10:00:00Z",
    },
    {
        "reviewId": "mock-002",
        "name": "accounts/000/locations/000/reviews/mock-002",
        "starRating": "TWO",
        "reviewer": {"displayName": "Carlos Mendes"},
        "comment": "Fiquei bem decepcionado. O prazo não foi cumprido e a comunicação foi péssima. Esperava mais de uma empresa com esse nome.",
        "createTime": "2026-05-13T15:30:00Z",
    },
    {
        "reviewId": "mock-003",
        "name": "accounts/000/locations/000/reviews/mock-003",
        "starRating": "FOUR",
        "reviewer": {"displayName": "Fernanda Lima"},
        "comment": "Bom atendimento no geral. O trabalho ficou bonito, só achei o prazo um pouco longo. Mas recomendo.",
        "createTime": "2026-05-12T09:15:00Z",
    },
    {
        "reviewId": "mock-004",
        "name": "accounts/000/locations/000/reviews/mock-004",
        "starRating": "ONE",
        "reviewer": {"displayName": "Roberto Alves"},
        "comment": "Péssima experiência. Cobrei retorno por semanas e ninguém me respondeu. Nunca mais.",
        "createTime": "2026-05-11T18:00:00Z",
    },
    {
        "reviewId": "mock-005",
        "name": "accounts/000/locations/000/reviews/mock-005",
        "starRating": "FIVE",
        "reviewer": {"displayName": "Juliana Castro"},
        "comment": "Produziu o vídeo institucional da nossa empresa e ficou perfeito. Profissionais de verdade!",
        "createTime": "2026-05-10T11:45:00Z",
    },
]
