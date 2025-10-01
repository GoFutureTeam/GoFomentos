import React from 'react';
const Footer = () => {
  const handleEmailClick = () => {
    window.location.href = 'mailto:contatogofuture@gmail.com';
  };
  return <footer className="relative">
      <img src="https://cdn.builder.io/api/v1/image/assets/f302f4804c934a9ca3c4b476c31d8232/ad372249cc6b66a82a42a2df50cde3994761ac19?placeholderIfAbsent=true" alt="Background" className="absolute inset-0 w-full h-full object-cover" />
      
      <div style={{
      backgroundImage: 'url(/lovable-uploads/b4c4ad04-bb19-4771-8f0c-712bf67d01f5.png)',
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat'
    }} className="relative rounded-none">
        <div className="flex flex-col lg:flex-row items-center justify-center gap-8 py-8 px-8 max-w-4xl mx-auto">
          <div className="text-center">
            <p className="font-archivo font-medium italic text-black text-lg mb-1">
              Quer mais informações? Entre em contato!
            </p>
            <h2 className="text-[rgba(67,80,88,1)] text-2xl lg:text-3xl font-extrabold">
              Fale com a nossa equipe
            </h2>
          </div>
          
          <button onClick={handleEmailClick} className="bg-white text-black text-base font-medium px-6 py-3 rounded-[25px] flex-shrink-0 hover:bg-gray-50 transition-colors">
            E-mail: contatogofuture@gmail.com
          </button>
        </div>
        
        <div className="bg-[rgba(67,80,88,1)] py-4 px-[70px] text-center">
          <p className="text-[rgba(248,248,248,1)] text-sm font-medium">
            Copyright © 2025 Powered by GoFuture - Todos os direitos reservados.
          </p>
        </div>
      </div>
    </footer>;
};
export default Footer;