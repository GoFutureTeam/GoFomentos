import React from "react";

const InfoSection = () => {
  return (
    <section className="flex flex-col relative z-10 w-full text-[rgba(67,80,88,1)]">
      <img
        src="https://cdn.builder.io/api/v1/image/assets/f302f4804c934a9ca3c4b476c31d8232/fbc65390241f67ef03bdad9dbf7915b568ede057?placeholderIfAbsent=true"
        alt="Background"
        className="absolute h-full w-full object-cover inset-0"
      />
      <div className="relative bg-[rgba(220,247,99,0.65)] z-10 flex w-full flex-col items-center py-12 sm:py-16 lg:py-20 px-5 lg:px-[70px]">
        <div className="flex w-full max-w-[1279px] items-stretch gap-8 lg:gap-[100px] flex-col lg:flex-row text-center lg:text-left">
          <h2 className="text-2xl sm:text-3xl lg:text-[32px] font-extrabold lg:w-[273px] lg:shrink-0 text-[#435058]">
            Você sabe porque se inscrever em Editais?
          </h2>
          <p className="text-lg sm:text-xl font-medium leading-6 sm:leading-[30px] flex-1 text-[#435058]">
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

export default InfoSection;
