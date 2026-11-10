/* ==========================================================================
   MEGA MOTORS - DADOS DO SITE
   Edite SOMENTE este arquivo para trocar textos, produtos, preços e fotos.
   Tudo que está entre [COLCHETES] é um marcador: troque pelo texto real.
   Cuidado: mantenha as aspas "..." e as vírgulas no fim de cada linha.
   As fotos ficam na pasta "imagens". Basta escrever aqui o nome do arquivo.
   Se a foto não existir, o site mostra um espaço reservado no lugar.
   ========================================================================== */

const DADOS = {

  /* ---------- DADOS DA LOJA ---------- */
  loja: {
    nome: "Mega Motors",
    segmento: "Mobilidade Elétrica",
    frase: "A forma inteligente de se locomover",
    endereco: "Av. São José dos Campos, 2410 - Parque São Martinho, Campinas - SP",
    horario: [
      { dia: "Segunda a sexta", horas: "9h às 19h" },
      { dia: "Sábado", horas: "9h às 17h" }
    ],
    whatsapp: "5519999499216",          // só números, com 55 + DDD
    whatsappExibicao: "(19) 99949-9216",
    email: "[EMAIL]",                    // troque pelo e-mail real
    instagram: "@megamotors.eletrica",
    instagramUrl: "https://www.instagram.com/megamotors.eletrica/",
    googleAvaliacaoUrl: "",              // [LINK DE AVALIAÇÃO DO GOOGLE] cole aqui o link
    fotoFachada: "fachada.jpg"
  },

  /* ---------- MENSAGENS PRONTAS DO WHATSAPP ---------- */
  mensagens: {
    geral: "Olá! Vim pelo site da Mega Motors e gostaria de mais informações.",
    interesse: "Olá! Tenho interesse no modelo {NOME}. Como posso fazer?",   // {NOME} vira o nome do produto
    testDrive: "Olá! Gostaria de agendar um test drive. Quais modelos e horários estão disponíveis?",
    avaliacao: "Olá! Gostaria de agendar uma avaliação na assistência técnica. Como posso fazer?",
    trabalhe: "Olá! Tenho interesse em trabalhar na Mega Motors. Como posso enviar meu currículo?",
    parceria: "Olá! Gostaria de falar sobre uma parceria com a Mega Motors."
  },

  /* ---------- CATEGORIAS DO CATÁLOGO ---------- */
  // "id" é usado nos produtos (campo "categoria"). Não repita ids.
  categorias: [
    { id: "scooters",  nome: "Scooters" },
    { id: "bikes",     nome: "Bikes elétricas" },
    { id: "patinetes", nome: "Patinetes" },
    { id: "triciclos", nome: "Triciclos" },
    { id: "infantis",  nome: "Infantis" },
    { id: "capacetes", nome: "Capacetes" }
  ],

  /* ---------- PRODUTOS NOVOS ---------- */
  // Para adicionar um produto, copie uma linha { ... } e cole abaixo dela.
  // Campos vazios ("") não aparecem no card (ex.: capacete não tem autonomia).
  produtos: [
    { categoria: "scooters",  nome: "[MODELO 1]", potencia: "[POTÊNCIA]", autonomia: "[AUTONOMIA]", foto: "scooter-1.jpg" },
    { categoria: "bikes",     nome: "[MODELO 2]", potencia: "[POTÊNCIA]", autonomia: "[AUTONOMIA]", foto: "bike-1.jpg" },
    { categoria: "patinetes", nome: "[MODELO 3]", potencia: "[POTÊNCIA]", autonomia: "[AUTONOMIA]", foto: "patinete-1.jpg" },
    { categoria: "triciclos", nome: "[MODELO 4]", potencia: "[POTÊNCIA]", autonomia: "[AUTONOMIA]", foto: "triciclo-1.jpg" },
    { categoria: "infantis",  nome: "[MODELO 5]", potencia: "[POTÊNCIA]", autonomia: "[AUTONOMIA]", foto: "infantil-1.jpg" },
    { categoria: "capacetes", nome: "[MODELO 6]", potencia: "", autonomia: "", foto: "capacete-1.jpg" }
  ],

  /* ---------- SEMINOVOS E CONSIGNADOS ---------- */
  // "condicao": escreva "Seminovo" ou "Consignado" (aparece como selo no card).
  seminovos: [
    { condicao: "Seminovo",   nome: "[MODELO SEMINOVO 1]",   potencia: "[POTÊNCIA]", autonomia: "[AUTONOMIA]", foto: "seminovo-1.jpg" },
    { condicao: "Consignado", nome: "[MODELO CONSIGNADO 1]", potencia: "[POTÊNCIA]", autonomia: "[AUTONOMIA]", foto: "seminovo-2.jpg" },
    { condicao: "Seminovo",   nome: "[MODELO SEMINOVO 2]",   potencia: "[POTÊNCIA]", autonomia: "[AUTONOMIA]", foto: "seminovo-3.jpg" }
  ],

  /* ---------- ASSISTÊNCIA TÉCNICA ---------- */
  assistencia: {
    texto: "Atendemos também outras marcas.",
    servicos: [
      { servico: "[SERVIÇO 1]", preco: "[PREÇO]" },
      { servico: "[SERVIÇO 2]", preco: "[PREÇO]" },
      { servico: "[SERVIÇO 3]", preco: "[PREÇO]" },
      { servico: "[SERVIÇO 4]", preco: "[PREÇO]" },
      { servico: "[SERVIÇO 5]", preco: "[PREÇO]" }
    ],
    observacao: "[OBSERVAÇÃO SOBRE OS PREÇOS, ex.: valores a partir de, mão de obra, peças à parte]"
  },

  /* ---------- VÍDEOS DE MANUTENÇÃO (INSTAGRAM) ---------- */
  // Em "link" cole o endereço do post ou reel, ex.: "https://www.instagram.com/reel/XXXXXXXX/"
  // Enquanto o link estiver vazio, aparece um espaço reservado.
  videos: [
    { titulo: "[VÍDEO 1]", link: "" },
    { titulo: "[VÍDEO 2]", link: "" },
    { titulo: "[VÍDEO 3]", link: "" }
  ],

  /* ---------- SOBRE NÓS ---------- */
  sobre: {
    texto: [
      "A Mega Motors é uma loja de mobilidade elétrica em Campinas - SP. Trabalhamos com scooters, bikes elétricas, patinetes, triciclos, modelos infantis e capacetes, e temos assistência técnica para várias marcas.",
      "[TEXTO SOBRE A LOJA: história, tempo de mercado, diferenciais]"
    ],
    fotos: [
      { arquivo: "loja-1.jpg",   legenda: "Nossa loja" },
      { arquivo: "loja-2.jpg",   legenda: "Nossa loja" },
      { arquivo: "equipe-1.jpg", legenda: "Nossa equipe" },
      { arquivo: "equipe-2.jpg", legenda: "Nossa equipe" }
    ]
  },

  /* ---------- BENEFÍCIOS ---------- */
  beneficios: [
    { icone: "💰", titulo: "Economia",       texto: "Gaste menos para se locomover no dia a dia. [DETALHE]" },
    { icone: "⚡", titulo: "Praticidade",    texto: "Mais agilidade no trânsito e facilidade para estacionar. [DETALHE]" },
    { icone: "🔌", titulo: "Sem combustível", texto: "Recarregue na tomada, sem parar no posto. [DETALHE]" }
  ],

  /* ---------- FEEDBACKS DE CLIENTES ---------- */
  feedbacks: {
    fotos: ["cliente-1.jpg", "cliente-2.jpg", "cliente-3.jpg", "cliente-4.jpg", "cliente-5.jpg", "cliente-6.jpg"]
  },

  /* ---------- PERGUNTAS FREQUENTES (chat sem IA) ---------- */
  // Troque cada "[RESPOSTA]" pelo texto real. Para tirar uma pergunta, apague a linha.
  perguntas: [
    { pergunta: "Qual o horário de funcionamento?",
      resposta: "Atendemos de segunda a sexta, das 9h às 19h, e aos sábados, das 9h às 17h." },
    { pergunta: "Qual a autonomia?",              resposta: "[RESPOSTA]" },
    { pergunta: "Quanto tempo leva para carregar?", resposta: "[RESPOSTA]" },
    { pergunta: "Qual a garantia?",               resposta: "[RESPOSTA]" },
    { pergunta: "Quais as formas de pagamento?",  resposta: "[RESPOSTA]" },
    { pergunta: "Precisa de habilitação?",        resposta: "[RESPOSTA]" },
    { pergunta: "Precisa emplacar?",              resposta: "[RESPOSTA]" }
  ],

  /* ---------- PARCERIAS ---------- */
  // "logo" é o nome do arquivo na pasta imagens. "link" é opcional (site ou Instagram do parceiro).
  parceiros: [
    { nome: "[PARCEIRO 1]", logo: "parceiro-1.png", link: "" },
    { nome: "[PARCEIRO 2]", logo: "parceiro-2.png", link: "" },
    { nome: "[PARCEIRO 3]", logo: "parceiro-3.png", link: "" },
    { nome: "[PARCEIRO 4]", logo: "parceiro-4.png", link: "" }
  ]
};
