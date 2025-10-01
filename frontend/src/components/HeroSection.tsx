import React from "react";
const HeroSection: React.FC = () => {
  return (
    <section className="bg-[rgba(67,80,88,1)]">
      <div
        style={{
          backgroundImage:
            "url(/lovable-uploads/fc8e9f15-312d-4438-9834-cd7b3554cb1d.png)",
          backgroundSize: "auto 100%",
          backgroundPosition: "right center",
          backgroundRepeat: "no-repeat",
        }}
        className="px-5 py-12 lg:py-16 relative lg:px-20"
      >
        <div className="w-full max-w-[1279px] mx-auto">
          <div className="flex gap-8 flex-col lg:flex-row items-center">
            <div className="w-full lg:w-[65%]">
              <h1 className="text-white text-4xl sm:text-5xl font-black leading-tight tracking-wide mb-6">
                Soluções para alavancar a inovação em sua empresa
              </h1>
              <p className="text-white text-lg sm:text-xl font-normal leading-7 sm:leading-8 max-w-2xl">
                Conheça os instrumentos de apoio à inovação disponíveis e
                selecione os mais adequados ao seu projeto.
              </p>
            </div>
          </div>
        </div>
      </div>

      <div
        style={{
          backgroundImage:
            "url(/lovable-uploads/8a170130-d07b-497a-9e68-ec6bb3ce56bb.png)",
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat",
        }}
        className="relative bg-[rgba(220,247,99,0.65)] z-10 flex w-full flex-col items-center py-12 sm:py-16 px-5 lg:px-20 lg:py-[20px]"
      >
        <div className="flex w-full max-w-[1279px] flex-row justify-between items-start gap-8 px-5 lg:px-[10px]">
          <h2 className="font-archivo font-extrabold text-2xl sm:text-3xl lg:w-auto lg:max-w-[400px] lg:shrink-0 text-[#435058] mx-0 my-0 text-left px-0 py-[20px]">
            Você sabe porque se inscrever em Editais?
          </h2>
          <p className="font-archivo font-medium text-lg sm:text-xl leading-6 sm:leading-[30px] flex-1 text-[#435058] py-[6px]">
            Participar de editais de fomento é uma das formas mais estratégicas
            de captar recursos, expandir projetos inovadores e ganhar
            visibilidade no seu setor. Com o Radar de Fomentos, você encontra as
            melhores oportunidades em um só lugar, com clareza e agilidade.
          </p>
        </div>
      </div>
    </section>
  );
};
export default HeroSection;
