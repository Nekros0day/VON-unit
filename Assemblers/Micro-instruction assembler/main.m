%randomvari
s=0;
%

chip1 = fopen('chip1.bin','w');
c1Data = zeros(1,32768,'uint8');

chip2 = fopen('chip2.bin','w');
c2Data = zeros(1,32768,'uint8');
% Micro instruction lists per chip
c1MicroIns1 = ["TD", "CR", "JMP", "MI", "FI", "RI", "AD1I", "AD2I", "AI", "BI", "CI", "DI", "II", "XinI", "YinI"];
c1MicroIns2 = ["EIO", "IRQDIS", "S4", "N/A", "HLT", "PU", "PD", "CE", "XinINC", "XinDEC", "YinINC", "YinDEC", "S5", "N/A", "N/A"];

c2MicroIns1 = ["RO", "ADO", "AO", "BO", "CO-", "DO", "EO", "XinO", "YinO", "STRO", "SERIALO", "RD", "SR", "INTV", "CO"];
c2MicroIns2 = ["S0", "S1", "S2", "S3"];

% Instructions per row, row one = LDA and so on.

Instructions = ["DC", "CO|MI", "RO|II|CE","ADO|MI","RO|AI","0","0"; 
                "DC", "CO|MI", "RO|II|CE","ADO|MI","RO|BI","0","0";
                "DC", "CO|MI", "RO|II|CE","ADO|MI","RO|CI","0","0";
                "DC", "CO|MI", "RO|II|CE","ADO|MI","RO|DI","0","0";
                "DC", "CO|MI", "RO|II|CE","ADO|MI","RO|XinI","0","0";
                "DC", "CO|MI", "RO|II|CE","ADO|MI","RO|YinI","0","0";
                "DC", "CO|MI", "RO|II|CE","CO|MI","RO|AD1I|CE","CO|MI","RO|AD2I|CE";
                "DC", "CO|MI", "RO|II|CE","ADO|MI","RO|BI","S3|S0|FI","S3|S0|AI|EO";
                "DC", "CO|MI", "RO|II|CE","ADO|MI","RO|BI","S2|S1|S5|FI","S2|S1|S5|AI|EO";
                "DC", "CO|MI", "RO|II|CE","ADO|MI","RO|BI","S2|S1|S4|FI","S2|S1|S4|AI|EO";
                "DC", "CO|MI", "RO|II|CE","EIO|AO|TD","AO|TD","0","0";
                "DC", "CO|MI", "RO|II|CE","AI|SERIALO","0","0","0";
                "DC", "CO|MI", "RO|II|CE","ADO|MI","AO|RI","0","0";
                "DC", "CO|MI", "RO|II|CE","ADO|JMP","0","0","0";
                "ZF", "CO|MI", "RO|II|CE","ADO|JMP","0","0","0";
                "XinZF", "CO|MI", "RO|II|CE","ADO|JMP","0","0","0";
                "YinZF", "CO|MI", "RO|II|CE","ADO|JMP","0","0","0";
                "DC", "CO|MI", "RO|II|CE","PU","ADO|JMP","0","0";
                "DC", "CO|MI", "RO|II|CE","PD","0","0","0";
                "DC", "CO|MI", "RO|II|CE","XinINC","0","0","0";
                "DC", "CO|MI", "RO|II|CE","YinINC","0","0","0";
                "DC", "CO|MI", "RO|II|CE","XinDEC","0","0","0";
                "DC", "CO|MI", "RO|II|CE","YinDEC","0","0","0";
                "DC", "CO|MI", "RO|II|CE", "IRQDIS","0","0","0";
                "DC", "CO|MI", "RO|II|CE", "HLT","0","0","0";
                "DC", "CO|MI", "RO|II|CE","CO|MI", "EIO|RO|CR","RO|CR|CE","0";
                "DC", "CO|MI", "RO|II|CE","S2|S1|S4|FI","0","0","0";
                "DC", "CO|MI", "RO|II|CE","CO|MI","RO|AI|CE","0","0";
                "DC", "CO|MI", "RO|II|CE","0","0","0","0";
                "DC", "CO|MI", "RO|II|CE","0","0","0","0";
                "DC", "CO|MI", "RO|II|CE","0","0","0","0";
                "DC", "CO|MI", "RO|II|CE","0","0","0","0";];
            
[InsRows,InsCols] = size(Instructions);

% JMP conditions Instructions
conditions = ["CF", "ZF", "AmBF", "APBF", "XinZF", "YinZF", "INT", "DC"];
JMPInstructions = ["ZF", "0", "0","0","0","0","0";];
            
[JInsRows,JInsCols] = size(JMPInstructions);
disp("Generating the instructions for Chip 1")
disp("Setting Fetch cycle")
% FETCH  
for i = 1:InsRows
    for j = 2:3
        C = strsplit(Instructions(i,j),'|');
        s = 0;
        for k = 1:length(C)
        
        if ~isempty(find(c1MicroIns1 == C(k), 1)) 
            s = s + find(c1MicroIns1 == C(k), 1);
        end
        if ~isempty(find(c1MicroIns2 == C(k), 1))
            s = s + bitshift((find(c1MicroIns2 == C(k), 1)),4);
        end
            for p = 1:128
                FlagStateAdress = bitshift(p-1,8);
                TstateAdress = bitshift(j-2,5);
                Adress = FlagStateAdress + TstateAdress + i;
                c1Data(Adress) = s;
            end
        end
    end
end
clc
disp("Generating the instructions for Chip 1")
disp("Setting Execute cycle")
% Data for CHIP 1
for i = 1:InsRows
    Fcon = find(conditions == Instructions(i,1), 1);
    for j = 2:InsCols
        C = strsplit(Instructions(i,j),'|');
        s = 0;
        for k = 1:length(C)
        
        if ~isempty(find(c1MicroIns1 == C(k), 1)) 
            s = s + find(c1MicroIns1 == C(k), 1);
        end
        if ~isempty(find(c1MicroIns2 == C(k), 1))
            s = s + bitshift((find(c1MicroIns2 == C(k), 1)),4);
        end
        
        end
        if Fcon == 8
            for p = 1:128
                FlagStateAdress = bitshift(p-1,8);
                TstateAdress = bitshift(j-2,5);
                Adress = FlagStateAdress + TstateAdress + i;
                c1Data(Adress) = s;
            end
        end
        if Fcon ~= 8
            for p = 1:128
                FlagStateAdress = bitshift(bitset(p-1, Fcon),8);
                TstateAdress = bitshift(j-2,5);
                Adress = FlagStateAdress + TstateAdress + i;
                c1Data(Adress) = s;
            end
        end
    end
end

clc
disp("Generating the instructions for Chip 1")
disp("Setting Interupt Request handler")

% Interupt sequance
IRQS = ["PU", "INTV|JMP","RD|EIO","RD","IRQDIS","0"];
            
[IRQRows,IRQCols] = size(IRQS);
for i = 1:IRQRows
    for j = 1:IRQCols
        C = strsplit(IRQS(i,j),'|');
        s = 0;
        for k = 1:length(C)
        
        if ~isempty(find(c1MicroIns1 == C(k), 1)) 
            s = s + find(c1MicroIns1 == C(k), 1);
        end
        if ~isempty(find(c1MicroIns2 == C(k), 1))
            s = s + bitshift((find(c1MicroIns2 == C(k), 1)),4);
        end
        
        end
        for r = 1:32
            for p = 1:64
                FlagStateAdress = bitshift(p-1,8);
                TstateAdress = bitshift(j-1,5);
                Adress = FlagStateAdress + TstateAdress + r-1 + 16384;
                c1Data(Adress) = s;
            end
        end
    end
end
clc
disp("Writing data for Chip 1")

fwrite(chip1,c1Data);

fclose(chip1);

clc
disp("Chip 1 completed as chip1.bin")
disp("Generating the instructions for Chip 2")
disp("Setting Fetch cycle")
% FETCH  
for i = 1:InsRows
    for j = 2:3
        C = strsplit(Instructions(i,j),'|');
        s = 0;
        for k = 1:length(C)
        
        if ~isempty(find(c2MicroIns1 == C(k), 1)) 
            s = s + find(c2MicroIns1 == C(k), 1);
        end
        if ~isempty(find(c2MicroIns2 == C(k), 1))
            F = find(c2MicroIns2 == C(k), 1) - 1 ;
            s = s + bitshift(2^F,4);
        end
            for p = 1:128
                FlagStateAdress = bitshift(p-1,8);
                TstateAdress = bitshift(j-2,5);
                Adress = FlagStateAdress + TstateAdress + i;
                c2Data(Adress) = s;
            end
        end
    end
end
clc
disp("Generating the instructions for Chip 2")
disp("Setting Execute cycle")

% Data for CHIP 2
for i = 1:InsRows
    Fcon = find(conditions == Instructions(i,1), 1);
    for j = 2:InsCols
        C = strsplit(Instructions(i,j),'|');
        s = 0;
        for k = 1:length(C)
        
        if ~isempty(find(c2MicroIns1 == C(k), 1)) 
            s = s + find(c2MicroIns1 == C(k), 1);
        end
        if ~isempty(find(c2MicroIns2 == C(k), 1))
            F = find(c2MicroIns2 == C(k), 1) - 1 ;
            s = s + bitshift(2^F,4);
        end
        
        end
        if Fcon == 8
            for p = 1:128
                FlagStateAdress = bitshift(p-1,8);
                TstateAdress = bitshift(j-2,5);
                Adress = FlagStateAdress + TstateAdress + i;
                c2Data(Adress) = s;
            end
        end
        if Fcon ~= 8
            for p = 1:128
                FlagStateAdress = bitshift(bitset(p-1, Fcon),8);
                TstateAdress = bitshift(j-2,5);
                Adress = FlagStateAdress + TstateAdress + i;
                c2Data(Adress) = s;
            end
        end
        
    end
end
clc
disp("Generating the instructions for Chip 2")
disp("Setting Interupt Request handler")

% Interupt sequance
IRQS = ["PU", "INTV|JMP","RD|EIO","RD","IRQDIS","0"];
            
[IRQRows,IRQCols] = size(IRQS);
for i = 1:IRQRows
    for j = 1:IRQCols
        C = strsplit(IRQS(i,j),'|');
        s = 0;
        for k = 1:length(C)
        
        if ~isempty(find(c2MicroIns1 == C(k), 1)) 
            s = s + find(c2MicroIns1 == C(k), 1);
        end
        if ~isempty(find(c2MicroIns2 == C(k), 1))
            s = s + bitshift((find(c2MicroIns2 == C(k), 1)),4);
        end
        
        end
        for r = 1:32
            for p = 1:64
                FlagStateAdress = bitshift(p-1,8);
                TstateAdress = bitshift(j-1,5);
                Adress = FlagStateAdress + TstateAdress + r-1 + 16384;
                c2Data(Adress) = s;
            end
        end
    end
end
clc
disp("Writing data for Chip 2")
fwrite(chip2,c2Data);

fclose(chip2);
clc
disp("Chip 2 completed as chip2.bin")
clc
disp("All Done")