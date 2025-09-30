import React from 'react';
import CommonHeader from '../components/CommonHeader';
import { EmailSignup as EmailSignupForm } from '../components/match/EmailSignup';
import Footer from '../components/details/Footer';

const EmailSignup = () => {
  return (
    <div className="overflow-hidden">
      <CommonHeader 
        title="Cadastre-se e receba atualizações no seu e-mail"
        description="Cadastre seu email e seja notificado automaticamente sempre que um novo edital compatível com seu projeto for publicado!"
        showSecondSection={false}
      />
      
      <div style={{
        backgroundImage: 'url(/lovable-uploads/8a170130-d07b-497a-9e68-ec6bb3ce56bb.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      }} className="relative bg-[rgba(220,247,99,0.65)] z-10 flex w-full flex-col items-center py-12 sm:py-16 px-5 lg:px-20 lg:py-[20px]" />
      
      <main>
        <EmailSignupForm />
      </main>
      
      <Footer />
    </div>
  );
};

export default EmailSignup;