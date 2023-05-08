
body = """
		<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xn="http://xmlns.cenace.com/">
	        <soapenv:Header>
	            <xn:Authentication>
	                <!--Optional:-->
	                <xn:userNameToken>BTMNN</xn:userNameToken>
	                <!--Optional:-->
	                <xn:passwordToken>Beetm2023$</xn:passwordToken>
	                <!--Optional:-->
	                <xn:hd>9253798B5209E6B97F6BDE4CB414FFA1BE207E68</xn:hd>
	            </xn:Authentication>
	        </soapenv:Header>
	        <soapenv:Body>
	            <xn:enviarOfertaCompraEnergia>
	                <!--Optional:-->
	                <xn:clvParticipante>C038</xn:clvParticipante>
	                <!--Optional:-->
	                <xn:fechaInicial>%s</xn:fechaInicial>
	                <!--Optional:-->
	                <xn:fechaFinal>%s</xn:fechaFinal>
	                <!--Optional:-->
	                <xn:clvCarga>%s</xn:clvCarga>
	                <!--Optional:-->
	                <xn:clvSistema>SIN</xn:clvSistema>
	                <!--Optional:-->
	                <xn:jsonOE>{ 
	        "ofertaEconomica": [ 
	        { 
	        "hora": 1, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        },
	        { 
	        "hora": 2, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        }
	        ,
	        { 
	        "hora": 3, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        }
	        ,
	        { 
	        "hora": 4, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        }
	        ,
	        { 
	        "hora": 5, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        }
	        ,
	        { 
	        "hora": 6, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        }
	        ,
	        { 
	        "hora": 7, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        }
	        ,
	        { 
	        "hora": 8, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        }
	        ,
	        { 
	        "hora": 9, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        }
	        ,
	        { 
	        "hora": 10, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        }
	        ,
	        { 
	        "hora": 11, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        }
	        ,
	        { 
	        "hora": 12, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        }
	        ,
	        { 
	        "hora": 13, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        }
	        ,
	        { 
	        "hora": 14, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        }
	        ,
	        { 
	        "hora": 15, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        }
	        ,
	        { 
	        "hora": 16, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        }
	        ,
	        { 
	        "hora": 17, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        }
	        ,
	        { 
	        "hora": 18, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        }
	        ,
	        { 
	        "hora": 19, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        }
	        ,
	        { 
	        "hora": 20, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        }
	        ,
	        { 
	        "hora": 21, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        }
	        ,
	        { 
	        "hora": 22, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        }
	        ,
	        { 
	        "hora": 23, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        }
	        ,
	        { 
	        "hora": 24, 
	        "idSubInt": 1, 
	        "demandaFijaMw": %s, 
	        "oiMw01": 0.0, 
	        "oiPrecio01": 0.0, 
	        "oiMw02": 0.0, 
	        "oiPrecio02": 0.0, 
	        "oiMw03": 0.0, 
	        "oiPrecio03": 0.0

	        }
	        ] 
	        }

	        </xn:jsonOE>
	            </xn:enviarOfertaCompraEnergia>
	        </soapenv:Body>
	        </soapenv:Envelope>
	    """