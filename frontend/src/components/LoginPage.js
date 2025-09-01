import React, { useState } from 'react';
import RequestOtp from './RequestOtp';
import VerifyOtp from './VerifyOtp';

function LoginPage() {
    const [step, setStep] = useState(1);
    const [identifier, setIdentifier] = useState('');

    const handleOtpSent = (sentIdentifier) => {
        setIdentifier(sentIdentifier);
        setStep(2);
    };

    if (step === 1) {
        return <RequestOtp onOtpSent={handleOtpSent} />;
    }

    return <VerifyOtp identifier={identifier} />;
}

export default LoginPage;