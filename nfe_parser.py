import xml.etree.ElementTree as ET
from datetime import datetime

class NFeParse:
    def __init__(self, xml_string):
        # 定义命名空间
        self.ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        # 解析XML
        self.root = ET.fromstring(xml_string)
        self.inf_nfe = self.root.find('nfe:infNFe', self.ns)

    def calculate_bling_total(self):
        """计算Bling税务系统的最终票据计算价格"""
        total = self.inf_nfe.find('nfe:total/nfe:ICMSTot', self.ns)
        produtos = float(total.find('nfe:vProd', self.ns).text)
        frete = float(total.find('nfe:vFrete', self.ns).text)
        outras = float(total.find('nfe:vOutro', self.ns).text)
        return produtos + frete + outras

    def calculate_tax_total(self):
        """计算总税金"""
        total = self.inf_nfe.find('nfe:total/nfe:ICMSTot', self.ns)
        ii = float(total.find('nfe:vII', self.ns).text)
        ipi = float(total.find('nfe:vIPI', self.ns).text)
        pis = float(total.find('nfe:vPIS', self.ns).text)
        cofins = float(total.find('nfe:vCOFINS', self.ns).text)
        icms = float(total.find('nfe:vICMS', self.ns).text)
        return ii + ipi + pis + cofins + icms

    def get_basic_info(self):
        """获取基本信息"""
        ide = self.inf_nfe.find('nfe:ide', self.ns)
        total = self.inf_nfe.find('nfe:total/nfe:ICMSTot', self.ns)
        
        # 计算Bling系统总价
        bling_total = self.calculate_bling_total()
        
        # 计算税金总额
        tax_total = self.calculate_tax_total()
        
        return {
            'NFe号码': self.inf_nfe.get('Id'),
            '发票号码': ide.find('nfe:nNF', self.ns).text,
            '发票系列': ide.find('nfe:serie', self.ns).text,
            '发票日期': ide.find('nfe:dhEmi', self.ns).text,
            '操作性质': ide.find('nfe:natOp', self.ns).text,
            '发票模式': ide.find('nfe:mod', self.ns).text,
            '发票类型': ide.find('nfe:tpNF', self.ns).text,
            '目的地': ide.find('nfe:idDest', self.ns).text,
            '环境类型': ide.find('nfe:tpAmb', self.ns).text,
            '发票目的': ide.find('nfe:finNFe', self.ns).text,
            '消费者类型': ide.find('nfe:indFinal', self.ns).text,
            '交易方式': ide.find('nfe:indPres', self.ns).text,
            '处理版本': ide.find('nfe:verProc', self.ns).text,
            '重要计算结果': {
                'Bling系统最终价格': {
                    '商品总价': float(total.find('nfe:vProd', self.ns).text),
                    '运费': float(total.find('nfe:vFrete', self.ns).text),
                    '其他费用': float(total.find('nfe:vOutro', self.ns).text),
                    '最终总价': bling_total
                },
                '税金总额': {
                    'II(进口税)': float(total.find('nfe:vII', self.ns).text),
                    'IPI': float(total.find('nfe:vIPI', self.ns).text),
                    'PIS': float(total.find('nfe:vPIS', self.ns).text),
                    'COFINS': float(total.find('nfe:vCOFINS', self.ns).text),
                    'ICMS': float(total.find('nfe:vICMS', self.ns).text),
                    '税金合计': tax_total
                }
            }
        }

    def get_emitter_info(self):
        """获取发票方详细信息"""
        emit = self.inf_nfe.find('nfe:emit', self.ns)
        enderEmit = emit.find('nfe:enderEmit', self.ns)
        return {
            '公司名称': emit.find('nfe:xNome', self.ns).text,
            'CNPJ': emit.find('nfe:CNPJ', self.ns).text,
            '商业名称': emit.find('nfe:xFant', self.ns).text,
            '地址': {
                '街道': enderEmit.find('nfe:xLgr', self.ns).text,
                '门牌号': enderEmit.find('nfe:nro', self.ns).text,
                '区域': enderEmit.find('nfe:xBairro', self.ns).text,
                '城市代码': enderEmit.find('nfe:cMun', self.ns).text,
                '城市': enderEmit.find('nfe:xMun', self.ns).text,
                '州': enderEmit.find('nfe:UF', self.ns).text,
                '邮编': enderEmit.find('nfe:CEP', self.ns).text,
                '国家代码': enderEmit.find('nfe:cPais', self.ns).text,
                '国家': enderEmit.find('nfe:xPais', self.ns).text,
                '电话': enderEmit.find('nfe:fone', self.ns).text
            },
            '纳税制度': emit.find('nfe:CRT', self.ns).text if emit.find('nfe:CRT', self.ns) is not None else 'N/A'
        }

    def get_recipient_info(self):
        """获取收票方详细信息"""
        dest = self.inf_nfe.find('nfe:dest', self.ns)
        enderDest = dest.find('nfe:enderDest', self.ns)
        return {
            '公司名称': dest.find('nfe:xNome', self.ns).text,
            '外国身份': dest.find('nfe:idEstrangeiro', self.ns).text if dest.find('nfe:idEstrangeiro', self.ns) is not None else 'N/A',
            '地址': {
                '街道': enderDest.find('nfe:xLgr', self.ns).text,
                '门牌号': enderDest.find('nfe:nro', self.ns).text,
                '区域': enderDest.find('nfe:xBairro', self.ns).text if enderDest.find('nfe:xBairro', self.ns) is not None else 'N/A',
                '城市代码': enderDest.find('nfe:cMun', self.ns).text,
                '城市': enderDest.find('nfe:xMun', self.ns).text,
                '州': enderDest.find('nfe:UF', self.ns).text,
                '邮编': enderDest.find('nfe:CEP', self.ns).text,
                '国家代码': enderDest.find('nfe:cPais', self.ns).text,
                '国家': enderDest.find('nfe:xPais', self.ns).text
            },
            'IE状态': dest.find('nfe:indIEDest', self.ns).text
        }

    def get_products(self):
        """获取商品详细信息"""
        products = []
        for det in self.inf_nfe.findall('nfe:det', self.ns):
            prod = det.find('nfe:prod', self.ns)
            
            # 获取DI信息（如果存在）
            di_info = {}
            di = prod.find('nfe:DI', self.ns)
            if di is not None:
                di_info = {
                    'DI号码': di.find('nfe:nDI', self.ns).text,
                    'DI日期': di.find('nfe:dDI', self.ns).text,
                    '通关地点': di.find('nfe:xLocDesemb', self.ns).text,
                    '通关州': di.find('nfe:UFDesemb', self.ns).text,
                    '通关日期': di.find('nfe:dDesemb', self.ns).text,
                    '运输方式': di.find('nfe:tpViaTransp', self.ns).text,
                    '出口商': di.find('nfe:cExportador', self.ns).text
                }

            # 获取税收信息
            imposto = det.find('nfe:imposto', self.ns)
            tax_info = {}
            
            # ICMS信息
            icms = imposto.find('.//nfe:ICMS00', self.ns)
            if icms is not None:
                tax_info['ICMS'] = {
                    '原产地': icms.find('nfe:orig', self.ns).text,
                    'CST': icms.find('nfe:CST', self.ns).text,
                    '计算基础': float(icms.find('nfe:vBC', self.ns).text),
                    '税率': float(icms.find('nfe:pICMS', self.ns).text),
                    '税额': float(icms.find('nfe:vICMS', self.ns).text)
                }

            # PIS信息
            pis = imposto.find('.//nfe:PISAliq', self.ns)
            if pis is not None:
                tax_info['PIS'] = {
                    'CST': pis.find('nfe:CST', self.ns).text,
                    '计算基础': float(pis.find('nfe:vBC', self.ns).text),
                    '税率': float(pis.find('nfe:pPIS', self.ns).text),
                    '税额': float(pis.find('nfe:vPIS', self.ns).text)
                }

            # COFINS信息
            cofins = imposto.find('.//nfe:COFINSAliq', self.ns)
            if cofins is not None:
                tax_info['COFINS'] = {
                    'CST': cofins.find('nfe:CST', self.ns).text,
                    '计算基础': float(cofins.find('nfe:vBC', self.ns).text),
                    '税率': float(cofins.find('nfe:pCOFINS', self.ns).text),
                    '税额': float(cofins.find('nfe:vCOFINS', self.ns).text)
                }

            products.append({
                '商品代码': prod.find('nfe:cProd', self.ns).text,
                '商品描述': prod.find('nfe:xProd', self.ns).text,
                'NCM代码': prod.find('nfe:NCM', self.ns).text,
                'CFOP代码': prod.find('nfe:CFOP', self.ns).text,
                '单位': prod.find('nfe:uCom', self.ns).text,
                '数量': float(prod.find('nfe:qCom', self.ns).text),
                '单价': float(prod.find('nfe:vUnCom', self.ns).text),
                '总价': float(prod.find('nfe:vProd', self.ns).text),
                '运费': float(prod.find('nfe:vFrete', self.ns).text),
                '保险费': float(prod.find('nfe:vSeg', self.ns).text),
                '其他费用': float(prod.find('nfe:vOutro', self.ns).text),
                '进口信息': di_info if di_info else None,
                '税收信息': tax_info
            })
        return products

    def get_totals(self):
        """获取总计详细信息"""
        total = self.inf_nfe.find('nfe:total/nfe:ICMSTot', self.ns)
        return {
            'ICMS基础计算': float(total.find('nfe:vBC', self.ns).text),
            'ICMS金额': float(total.find('nfe:vICMS', self.ns).text),
            'ICMS豁免': float(total.find('nfe:vICMSDeson', self.ns).text),
            '商品总价': float(total.find('nfe:vProd', self.ns).text),
            '运费': float(total.find('nfe:vFrete', self.ns).text),
            '保险费': float(total.find('nfe:vSeg', self.ns).text),
            '折扣': float(total.find('nfe:vDesc', self.ns).text),
            '进口税': float(total.find('nfe:vII', self.ns).text),
            'IPI金额': float(total.find('nfe:vIPI', self.ns).text),
            'PIS金额': float(total.find('nfe:vPIS', self.ns).text),
            'COFINS金额': float(total.find('nfe:vCOFINS', self.ns).text),
            '其他费用': float(total.find('nfe:vOutro', self.ns).text),
            '发票总额': float(total.find('nfe:vNF', self.ns).text),
            '总税额': float(total.find('nfe:vTotTrib', self.ns).text)
        }

    def get_transport_info(self):
        """获取运输信息"""
        transp = self.inf_nfe.find('nfe:transp', self.ns)
        if transp is None:
            return None

        transport_info = {
            '运输方式': transp.find('nfe:modFrete', self.ns).text
        }

        # 运输公司信息
        transporta = transp.find('nfe:transporta', self.ns)
        if transporta is not None:
            transport_info['运输公司'] = {
                'CNPJ': transporta.find('nfe:CNPJ', self.ns).text if transporta.find('nfe:CNPJ', self.ns) is not None else 'N/A',
                '名称': transporta.find('nfe:xNome', self.ns).text if transporta.find('nfe:xNome', self.ns) is not None else 'N/A'
            }

        # 货物信息
        vol = transp.find('nfe:vol', self.ns)
        if vol is not None:
            transport_info['货物信息'] = {
                '数量': vol.find('nfe:qVol', self.ns).text if vol.find('nfe:qVol', self.ns) is not None else 'N/A',
                '包装类型': vol.find('nfe:esp', self.ns).text if vol.find('nfe:esp', self.ns) is not None else 'N/A',
                '净重': vol.find('nfe:pesoL', self.ns).text if vol.find('nfe:pesoL', self.ns) is not None else 'N/A',
                '毛重': vol.find('nfe:pesoB', self.ns).text if vol.find('nfe:pesoB', self.ns) is not None else 'N/A'
            }

        return transport_info

    def get_payment_info(self):
        """获取支付信息"""
        pag = self.inf_nfe.find('nfe:pag', self.ns)
        if pag is None:
            return None

        payment_info = []
        for detPag in pag.findall('nfe:detPag', self.ns):
            payment_info.append({
                '支付方式': detPag.find('nfe:tPag', self.ns).text,
                '支付金额': float(detPag.find('nfe:vPag', self.ns).text)
            })

        return payment_info

    def get_additional_info(self):
        """获取补充信息"""
        infAdic = self.inf_nfe.find('nfe:infAdic', self.ns)
        if infAdic is None:
            return None

        return {
            '补充信息': infAdic.find('nfe:infCpl', self.ns).text if infAdic.find('nfe:infCpl', self.ns) is not None else 'N/A'
        }

def format_value(value):
    """格式化数值输出"""
    if isinstance(value, float):
        return f"{value:,.2f}"
    return str(value)

def format_dict(d, indent=0):
    """格式化字典输出"""
    result = ""
    for key, value in d.items():
        if isinstance(value, dict):
            result += "  " * indent + f"{key}:\n"
            result += format_dict(value, indent + 1)
        else:
            result += "  " * indent + f"{key}: {format_value(value)}\n"
    return result

def main():
    # 从文件读取XML数据
    with open('nfe_example.xml', 'r', encoding='utf-8') as file:
        xml_data = file.read()

    # 创建解析器实例
    nfe = NFeParse(xml_data)

    # 打印基本信息
    print("\n=== 基本信息 ===")
    for key, value in nfe.get_basic_info().items():
        print(f"{key}: {value}")

    # 打印发票方信息
    print("\n=== 发票方信息 ===")
    for key, value in nfe.get_emitter_info().items():
        print(f"{key}: {value}")

    # 打印收票方信息
    print("\n=== 收票方信息 ===")
    for key, value in nfe.get_recipient_info().items():
        print(f"{key}: {value}")

    # 打印商品信息
    print("\n=== 商品信息 ===")
    for product in nfe.get_products():
        print("\n商品详情:")
        for key, value in product.items():
            print(f"{key}: {value}")

    # 打印总计信息
    print("\n=== 总计信息 ===")
    for key, value in nfe.get_totals().items():
        print(f"{key}: {value}")

if __name__ == '__main__':
    main() 